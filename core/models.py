from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils import timezone
import timedelta


# Single row to hold game state
class Game(models.Model):
    started = models.DateTimeField(null=True, blank=True)
    length = timedelta.TimedeltaField()

    @staticmethod
    def the_row():
        return Game.objects.get_or_create()[0]

    @staticmethod
    def has_started():
        return Game.the_row().started is not None

    @staticmethod
    def time_passed(delta):
        if not Game.has_started():
            return False
        return Game.the_row().started + delta <= timezone.now()

    @staticmethod
    def game_time():
        if not Game.has_started():
            return None
        return timezone.now() - Game.the_row().started

    @staticmethod
    def to_delta(date):
        if not Game.has_started():
            return None
        return date - Game.the_row().started

    @staticmethod
    def to_date(delta):
        if not Game.has_started():
            return None
        return Game.the_row().started + delta

    @staticmethod
    def start_now():
        if Game.has_started():
            raise Exception('Hra už běží.')
        g = Game.the_row()
        g.started = timezone.now()
        g.save()

    class Meta:
        permissions = (
            ("play", "Can play the game as a team"),
            ("control", "Can control the game through control panel"),
        )


class Team(models.Model):
    name = models.CharField(max_length=256, unique=True, verbose_name="Název týmu")
    visible = models.BooleanField(default=True)
    members = models.TextField(verbose_name="Seznam členů")

    def get_balance(self, entity) -> 'Balance':
        """
        Returns balance of a entity or creates new if not yet defined
        :rtype Balance
        """
        return self.balance_set.get_or_create(entity=entity)[0]

    def has_entity(self, entity):
        return self.get_balance(entity).total().amount > 0

    def assert_valid(self):
        """ If the current balance state is not valid, throws an exception. """
        not_enough = set()
        missing = set()
        for balance in self.balance_set.all():
            if not balance.is_valid():
                not_enough.add(balance.entity)
            missing.update(balance.licences_missing())
        if not_enough or missing:
            raise InvalidTransaction(not_enough, missing)

    def is_valid(self):
        """ Returns True if team's balance is in valid state """
        for balance in self.balance_set.all():
            if not balance.is_valid() or not balance.licences_satisfied():
                return False
        return True

    @property
    def inventory(self):
        return self.balance_set.order_by('entity__name')

    def __str__(self):
        return self.name


class Player(models.Model):
    user = models.OneToOneField(User)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        team_str = self.team.name if self.team else "no team"
        return self.user.username + " (" + team_str + ")"


class Status(models.Model):
    INFO = "info"
    WARNING = "warning"
    DANGER = "danger"
    SUCCESS = "success"
    TYPES = (
        (INFO, "Info (modrá)"),
        (WARNING, "Warning (žlutá)"),
        (DANGER, "Danger (červená)"),
        (SUCCESS, "Success (zelená)"),
    )
    time = timedelta.TimedeltaField()
    team = models.ForeignKey(Team, null=True, blank=True)
    type = models.CharField(max_length=32, choices=TYPES)
    message = models.TextField()

    def __str__(self):
        return "(%s) %s" % (self.team.name if self.team else "--", self.message)

    @staticmethod
    def visible():
        """
        Returns all statuses that are visible just now, and the time that means "now".
        """
        if not Game.has_started():
            return ([], 0)
        now = Game.game_time()
        data = Status.objects.filter(time__lte=now).order_by('-time')
        return (data, now)

    @staticmethod
    def add(message, type=INFO, team=None):
        time = Game.game_time()
        Status.objects.create(message=message, type=type, team=team, time=time)

    class Meta:
        verbose_name_plural = "Statuses"


class Entity(models.Model):
    name = models.CharField(max_length=128)
    units = models.CharField(max_length=128, blank=True)
    licences = models.ManyToManyField("self", symmetrical=False, related_name="licenced_entities")

    is_strategic = models.BooleanField(default=False)

    @property
    def is_licence(self):
        return self.licenced_entities.count() > 0

    @property
    def is_licenced(self):
        return self.licences.count() > 0

    def css_class(self):
        classes = []
        if self.is_strategic:
            classes.append("ent-strategic")
        if self.is_licence:
            classes.append("ent-licence")
        if self.is_licenced:
            classes.append("ent-needs-licence")
        return " ".join(classes)

    def __str__(self):
        classes = []
        if self.is_strategic:
            classes.append("(S) ")
        if self.is_licence:
            classes.append("(L) ")
        if self.is_licenced:
            classes.append("(D) ")
        return self.name + "".join(classes)

    class Meta:
        verbose_name_plural = "Entities"


class Quantity:
    """
    Helper class for pairs of entity and amount
    """

    def __repr__(self):
        return "%s (%s %s)" % (self.entity, self.amount, self.entity.units)

    def __str__(self):
        return "%i %s" % (self.amount, self.entity.units)

    def __int__(self):
        return self.amount

    def __init__(self, entity, amount):
        self.entity = entity
        self.amount = amount


class Balance(models.Model):
    team = models.ForeignKey(Team)
    entity = models.ForeignKey(Entity)
    amount = models.IntegerField(default=0)  # actual amount that can be sold
    blocked = models.IntegerField(default=0)  # amount expected to be sold

    """
    These are amounts that can be added in future by winning auction.
    expected > 0 means we need to keep all licences.
    expected_now is used to check situation, when team gets licenced entity and licences in the same time.
    blocked_now is used in situation when team sells both at a time.

    Please note that though we call if () then block(x) else expect(-x), we can not merge them,
    because negative values makes sense in both calls and must be separated. Expected values are invisible in UI.

    Note that *_now should be 0 unless in the middle of transaction.
    """
    expected = models.IntegerField(default=0)
    expected_now = models.IntegerField(default=0)
    blocked_now = models.IntegerField(default=0)

    def _all(self):
        return self.amount, self.blocked_now, self.blocked, self.expected, self.expected_now

    def total(self):
        return Quantity(self.entity, self.amount + self.blocked)

    def __str__(self):
        return "%s: %s (%d + %d blocked) %s" % (
            self.team.name, self.entity.name, self.amount, self.blocked, self.entity.units)

    def set_amount(self, amount: int):
        self.amount = amount
        return self

    def set_zero(self):
        self.amount = \
            self.blocked = self.blocked_now = \
            self.expected_now = self.expected = 0
        return self

    def all_zero(self):
        for a in self._all():
            if a != 0:
                return False
        return True

    def is_valid(self):
        return min(self.amount, self.blocked + self.blocked_now, self.expected + self.expected_now) >= 0

    def licenses_satisfied(self):
        return not self.licences_missing()

    def licences_missing(self):
        # ignoring blocked_now - do not require licence when selling everything
        if self.amount == 0 and self.blocked == 0 and self.expected + self.expected_now == 0:
            return []

        # get all licences that have amount and expected_now == 0, or those without balance with current team
        for l in self.entity.licences.all():
            bal = self.team.get_balance(l)
            if bal.amount == 0 and bal.expected_now == 0:
                yield l


    class Meta:
        unique_together = ("team", "entity")


class Transaction:
    class Operation:
        def __init__(self, team: Team, entity: Entity, amount=0, block=0, expect=0):
            self.team = team
            self.entity = entity
            self.amount = amount
            self.block = block
            self.expect = expect

        def commit(self):
            balance = self.team.get_balance(self.entity)
            balance.amount += self.amount
            if self.block > 0:
                balance.blocked_now += self.block
            else:
                balance.blocked += self.block
            if self.expect > 0:
                balance.expected_now += self.expect
            else:
                balance.expected += self.expect
            balance.save()
            return balance

        def after_validation(self):
            balance = self.team.get_balance(self.entity)
            balance.expected, balance.expected_now = balance.expected_now + balance.expected, 0
            balance.blocked, balance.blocked_now = balance.blocked_now + balance.blocked, 0
            balance.save()

        def __repr__(self):
            return "%r.%r += (%i, %i, %i)" % (self.team, self.entity, self.amount, self.block, self.expect)

    def __init__(self):
        self.operations = []
        self.reservations = []

    def block(self, team: Team, entity: Entity, amount: int):
        self.operations.append(Transaction.Operation(team, entity, amount=-amount, block=amount))
        return self

    def unblock(self, team: Team, entity: Entity, amount: int):
        return self.block(team, entity, -amount)

    def add(self, team: Team, entity: Entity, amount: int):
        self.operations.append(Transaction.Operation(team, entity, amount=amount))
        return self

    def remove(self, team: Team, entity: Entity, amount: int):
        return self.add(team, entity, -amount)

    def expect(self, team: Team, entity: Entity, amount: int):
        self.operations.append(Transaction.Operation(team, entity, expect=amount))
        return self

    def unexpect(self, team: Team, entity: Entity, amount: int):
        return self.expect(team, entity, -amount)

    def move(self, team_from: Team, team_to: Team, entity: Entity, amount: int):
        self.remove(team_from, entity, amount)
        self.add(team_to, entity, amount)
        return self

    def needs(self, team: Team, entity: Entity, amount: int):
        self.reservations.append((team, entity, amount))
        return self

    @transaction.atomic
    def commit(self):
        """
        Saves the updated balance back to the database.
        Consider this usage:
            with Transaction() as t:
                t.unblock(team, entity, amount)
                t.add(team, entity, amount)
        :raises InvalidTransaction in case the transaction is invalid
        """
        teams = set()

        for op in self.operations:
            op.commit()
            teams.add(op.team)

        not_enough = set()
        for (team, entity, amount) in self.reservations:
            bal = team.get_balance(entity)
            if (bal.amount + bal.expected_now) < amount:
                not_enough.add(entity)
        if not_enough:
            raise InvalidTransaction(not_enough)

        for team in teams:
            team.assert_valid()

        for op in self.operations:
            op.after_validation()

    def clean(self):
        """
        Performs dry commit and checks for errors, then rollbacks.
        :raises InvalidTransaction with error message if invalid.
        """

        @transaction.atomic
        def try_commit():
            self.commit()
            raise ValidTransaction  # = abort transaction

        try:
            try_commit()
        except ValidTransaction:
            pass

    def abort(self):
        self.operations = []
        self.reservations = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.commit()


class InvalidTransaction(Exception):

    def __init__(self, not_enough=[], missing_licences=[]):
        self.not_enough = list(not_enough)
        self.missing_licences = list(missing_licences)

    def __str__(self):
        err = ""
        if len(self.not_enough) == 1:
            err += "Nemáš dostatek %s." % ("".join(self.not_enough))
        elif len(self.not_enough) > 1:
            err += "Nemáš dostatek: %s." % (", ".join(self.not_enough))
        if len(self.missing_licences) == 1:
            return "Nemáš licenci %s" % (", ".join(self.missing_licences))
        elif len(self.missing_licences) > 1:
            return "Nemáš licence: %s" % (", ".join(self.missing_licences))

        if err == "":
            err = "Nějaká podivná chyba."

        return err


class ValidTransaction(Exception):
    """ Ugly hack. Look somewhere else, please. """
    pass
