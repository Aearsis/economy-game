from collections import defaultdict

from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils import timezone
from copy import deepcopy
import timedelta
# this was really problematic strange line
#from typing import List


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
        for balance in self.balance_set.all():
            if not balance.is_valid():
                raise InvalidTransaction(InvalidTransaction.ERR_NOT_ENOUGH, balance.entity)
            if not balance.licence_satisfied():
                raise InvalidTransaction(InvalidTransaction.ERR_NO_LICENCE, balance.entity)

    def is_valid(self):
        """ Returns True if team's balance is in valid state """
        for balance in self.balance_set.all():
            if not balance.is_valid() or not balance.licence_satisfied():
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

    class Meta:
        verbose_name_plural = "Statuses"


class Entity(models.Model):
    name = models.CharField(max_length=128)
    units = models.CharField(max_length=128, blank=True)
    licence = models.ForeignKey("self", null=True, blank=True)

    is_licence = models.BooleanField(default=False)
    is_strategic = models.BooleanField(default=False)

    @staticmethod
    def map_licences(entities):
        """
        Accepts a list of entities and returns a dictionary { entity E, list(entity depending on E }
        ( inverses licence mapping)
        """
        map = {}
        for entity in entities:
            if entity.licence:
                if entity.licence not in map:
                    map[entity.licence] = []
                map[entity.licence].append(entity)

        return map

    def css_class(self):
        classes = []
        if self.is_strategic:
            classes.append("ent-strategic")
        if self.is_licence:
            classes.append("ent-licence")
        if self.licence is not None:
            classes.append("ent-needs-licence")
        return " ".join(classes)

    def __str__(self):
        classes = []
        if self.is_strategic:
            classes.append("(S) ")
        if self.is_licence:
            classes.append("(L) ")
        if self.licence is not None:
            classes.append("(D) ")
        return "".join(classes) + self.name

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
    expected > 0 means we need to keep a licence.
    expected_now is used to check situation, when team gets licenced entity and the licence in the same time.
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

    def licence_satisfied(self):
        if self.entity.licence is None:
            return True
        # ignoring blocked_now - do not require licence when selling everything
        if self.amount == 0 and self.blocked == 0 and self.expected + self.expected_now == 0:
            return True

        lbalance = self.team.get_balance(self.entity.licence)
        # satisfy licence when buying it in the same transaction
        return lbalance.amount > 0 or lbalance.expected_now > 0

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

        for (team, entity, amount) in self.reservations:
            bal = team.get_balance(entity)
            if (bal.amount + bal.expected_now) < amount:
                raise InvalidTransaction(InvalidTransaction.ERR_NOT_ENOUGH, entity)

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
    ERR_NOT_ENOUGH = 1
    ERR_NO_LICENCE = 2

    def __init__(self, error, entity):
        self.error = error
        self.entity = entity

    def __str__(self):
        if self.error == self.ERR_NOT_ENOUGH:
            return "Nemáš dostatek " + str(self.entity)
        elif self.error == self.ERR_NO_LICENCE:
            return "Nemáš licenci pro " + str(self.entity) + "."
        else:
            return "Nějaká podivná chyba"


class ValidTransaction(Exception):
    """ Ugly hack. Look somewhere else, please. """
    pass
