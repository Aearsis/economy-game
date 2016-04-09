from collections import defaultdict

from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils import timezone
from copy import deepcopy
import timedelta
from typing import List


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
            if balance.amount < 0 or balance.blocked < 0:
                raise InvalidTransaction(InvalidTransaction.ERR_NOT_ENOUGH, balance.entity)
            licence = balance.entity.licence
            # we need to check only for non-blocked amount of licences
            need_licence = licence is not None and balance.total().amount > 0
            if need_licence and not self.has_entity(licence):
                raise InvalidTransaction(InvalidTransaction.ERR_NO_LICENCE, balance.entity)

    def is_valid(self):
        """ Returns True if team's balance is in valid state

        Catching exceptions is overkill, but this way we avoid duplicating code.
        """
        try:
            self.assert_valid()
        except InvalidTransaction:
            return False
        else:
            return True

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
        if self.licence != None:
            classes.append("ent-needs-licence")
        return " ".join(classes)

    def __str__(self):
        classes = []
        if self.is_strategic:
            classes.append("(S) ")
        if self.is_licence:
            classes.append("(L) ")
        if self.licence != None:
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
    amount = models.IntegerField(default=0)
    blocked = models.IntegerField(default=0)

    def total(self):
        return Quantity(self.entity, self.amount + self.blocked)

    def __str__(self):
        return "%s: %s (%d + %d blocked) %s" % (
        self.team.name, self.entity.name, self.amount, self.blocked, self.entity.units)

    def set_amount(self, amount: int):
        self.amount = amount
        return self

    class Meta:
        unique_together = ("team", "entity")


class Transaction:
    class Operation:
        def __init__(self, team: Team, entity: Entity, amount=0, block=0):
            self.team = team
            self.entity = entity
            self.amount = amount
            self.block = block

        def commit(self):
            balance = self.team.get_balance(self.entity)
            balance.amount += self.amount
            balance.blocked += self.block
            balance.save()

        def __repr__(self):
            return "%r.%r += (%i, %i)" % (self.team, self.entity, self.amount, self.block)

    def __init__(self):
        self.phases = []
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

    def move(self, team_from: Team, team_to: Team, entity: Entity, amount: int):
        self.remove(team_from, entity, amount)
        self.add(team_to, entity, amount)
        return self

    def needs(self, team: Team, entity: Entity, amount: int):
        self.reservations.append((team, entity, amount))
        return self

    def assertValidState(self):
        self.phases.append((self.operations, self.reservations))
        self.operations = []
        self.reservations = []

    @transaction.atomic
    def commit(self):
        """
        Saves the updated balance back to the database.
        Consider this usage:
            with Transaction() as t:
                t.unblock(team, entity, amount)
                t.add(team, entity, amount)
        :raises TransactionError in case the transaction is invalidreservations
        """
        self.assertValidState()

        for (operations, reservations) in self.phases:
            teams = set()

            for op in operations:
                op.commit()
                teams.add(op.team)

            for (team, entity, amount) in reservations:
                if team.get_balance(entity).total().amount < amount:
                    raise InvalidTransaction(InvalidTransaction.ERR_NOT_ENOUGH, entity)

            for team in teams:
                team.assert_valid()

        self.phases = []

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

    def __repr__(self):
        if self.error == self.ERR_NOT_ENOUGH:
            return "Nemáš dostatek " + self.entity
        elif self.error == self.ERR_NO_LICENCE:
            return "Nemáš licenci pro " + self.entity
        else:
            return "Nějaká podivná chyba"
