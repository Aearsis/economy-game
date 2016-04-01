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
        return Game.objects.get()

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
        return date-Game.the_row().started

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
            ("play_game", "Can play the game as a team"),
            ("control_game", "Can control the game through control panel"),
        )

class Team(models.Model):
    name = models.CharField(max_length=256, unique=True, verbose_name="Název týmu")
    visible = models.BooleanField(default=True)
    members = models.TextField(verbose_name="Seznam členů")

    balance_cache = None

    ### Team balance ###

    def get_balance(self, entity) -> 'Balance':
        """
        Returns balance of a entity or creates new if not yet defined
        :rtype Balance
        """
        balance = self.get_balance_cache()
        if entity not in balance:
            balance[entity] = Balance(team=self, entity=entity)

        return balance[entity]

    def get_balance_cache(self):
        """
        Returns team's complete balance
        :rtype dict(Entity, Balance)
        """
        if not self.balance_cache:
            bal_set = Balance.objects.filter(team=self)
            self.balance_cache = {balance.entity: balance for balance in bal_set}

        return self.balance_cache

    def check_balance(self, quantities: List['Quantity']):
        """
        Checks for (non-blocked) quantities of the team
        :raises InvalidTransaction if there is not enough entities
        """
        for quantity in quantities:
            if self.get_balance(quantity.entity).amount < quantity.amount:
                raise InvalidTransaction(InvalidTransaction.ERR_NOT_ENOUGH, quantity.entity)

    def __str__(self):
        return self.name


class Player(models.Model):
    user = models.OneToOneField(User)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        team_str = self.team.name if self.team else "no team"
        return self.user.username+" ("+team_str+")"


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
        data = Status.objects.filter(time__lte = now).order_by('-time')
        return (data, now)

    class Meta:
        verbose_name_plural = "Statuses"


class Entity(models.Model):
    name = models.CharField(max_length=128)
    units = models.CharField(max_length=128,blank=True)
    licence = models.ForeignKey("self", null=True, blank=True)

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

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Entities"


class Balance(models.Model):
    team = models.ForeignKey(Team)
    entity = models.ForeignKey(Entity)
    amount = models.PositiveIntegerField(default=0)
    blocked = models.PositiveIntegerField(default=0)
    reservation_cnt = models.PositiveSmallIntegerField(default=0)

    def total(self):
        return self.amount + self.blocked

    def __str__(self):
        return "%s: %s (%d + %d blocked) " % (self.team.name, self.entity.name, self.amount, self.blocked)

    class Meta:
        unique_together = ("team", "entity")


class Quantity:
    """
    Helper class for pairs of entity and amount
    """
    entity = Entity()
    amount = 0

    def __repr__(self):
        return "%s (%s %s)" % (self.entity, self.amount, self.entity.units)

    def __init__(self, entity, amount):
        self.entity = entity
        self.amount = amount


class Transaction:

    def __init__(self, team: Team):
        self.team = team
        self.balance_cache = deepcopy(team.get_balance_cache())

    def add(self, quantities: List[Quantity]):
        for quantity in quantities:
            self.__get_balance(quantity.entity).amount += quantity.amount

    def add_blocked(self, quantities: List[Quantity]):
        for quantity in quantities:
            self.__get_balance(quantity.entity).blocked += quantity.amount

    def remove(self, quantities: List[Quantity]):
        for quantity in quantities:
            self.__get_balance(quantity.entity).amount -= quantity.amount

    def remove_blocked(self, quantities: List[Quantity]):
        for quantity in quantities:
            self.__get_balance(quantity.entity).blocked -= quantity.amount

    def reserve(self, entities: List[Entity]):
        for entity in entities:
            self.__get_balance(entity).reservation_cnt += 1

    def unreserve(self, entities: List[Entity]):
        for entity in entities:
            balance = self.__get_balance(entity)
            balance.reservation_cnt = max(balance.reservation_cnt-1, 0)

    def check_valid(self):
        """
        Checks whether all subjects have a licence and their count is non-negative.
        :raises InvalidTransaction in case of failure
        """

        for balance in self.balance_cache.values():
            if balance.amount < 0 or balance.blocked < 0:
                raise InvalidTransaction(InvalidTransaction.ERR_NOT_ENOUGH, balance.entity)
            licence = balance.entity.licence
            need_licence = licence is not None and balance.total() > 0
            if need_licence and self.__get_balance(licence).amount <= 0:
                raise InvalidTransaction(InvalidTransaction.ERR_NO_LICENCE, balance.entity)
            if balance.reservation_cnt > 0 and balance.amount <= 1:
                raise InvalidTransaction(InvalidTransaction.ERR_RESERVED, balance.entity)

    @transaction.atomic
    def commit(self):
        """
        Saves the updated balance back to the database.
        NOTE: For committing more than one transaction at the time, use Transaction.commit_two -- otherwise,
        you may poison your balance cache.
        :raises TransactionError in case the transaction is invalid
        """
        self.check_valid()

        for balance in self.balance_cache.values():
            balance.save()
        self.team.balance_cache = self.balance_cache

    @staticmethod
    @transaction.atomic
    def commit_two(transaction1, transaction2):

        transaction1.check_valid()
        transaction2.check_valid()
        transaction1.commit()
        transaction2.commit()

    def __get_balance(self, entity: Entity) -> Balance:
        if entity not in self.balance_cache:
            self.balance_cache[entity] = Balance(entity=entity, team=self.team)
        return self.balance_cache[entity]


class InvalidTransaction(Exception):

    ERR_NOT_ENOUGH = 1
    ERR_NO_LICENCE = 2
    ERR_RESERVED = 3

    def __init__(self, error, entity):
        self.error = error
        self.entity = entity

    def __repr__(self):
        if self.error == self.ERR_NOT_ENOUGH:
            return "Chybí mi "+self.entity
        elif self.error == self.ERR_NO_LICENCE:
            return "Nemám licenci pro "+self.entity
        elif self.error == self.ERR_RESERVED:
            return self.entity+" je zarezervován, nemůžete ho úplně prodat"
        else:
            return "Nějaká podivná chyba"
