from django.db import models, transaction
from django.contrib.auth.models import User
from django.utils import timezone
from copy import deepcopy
import timedelta
from django.core.exceptions import ValidationError

# Single row to hold game state
class Game(models.Model):
    started = models.DateTimeField(null=True, blank=True)

    @staticmethod
    def the_row():
        return Game.objects.get(id=1)

    def has_started(self):
        return self.started is not None

    def time_passed(self, delta):
        return self.started + delta <= timezone.now()

    def game_time(self):
        return timezone.now() - self.started

    def to_delta(self, date):
        return date-self.started

    def to_date(self, delta):
        return self.started + delta


class Team(models.Model):
    name = models.CharField(max_length=256, unique=True)
    visible = models.BooleanField(default=False)
    balance = None


    ### Team balance ###

    def get_balance(self, entity):
        """
        Returns balance of a entity or creates new if not yet defined
        :rtype Balance
        """
        balance = self.get_balance_complete()
        if entity not in balance:
            balance[entity] = Balance(team=self, entity=entity)

        return balance[entity]

    def get_balance_complete(self):
        """
        Returns team's complete balance
        :rtype dict(Entity, Balance)
        """
        if not self.balance:
            bal_set = Balance.objects.filter(team=self)
            self.balance = { balance.entity:balance for balance in bal_set }

        return self.balance


    ### Trading and transferring entities

    @transaction.atomic
    def transfer(self, entities_amounts_in=[], entities_amounts_out=[], entities_amounts_check=[], \
                 in_blocked=False, out_blocked=False, pretend=False):
        """
            Transfers entities between teams or system.

            :param pretend: If set to True, checks whether the transaction is possible and returns bool.
                            If set to False, perform the transaction and raise ValidationError.
            :param entities_amounts_in: List of EntityAmounts which the team gives away
            :param entities_amounts_out: List of EntityAmounts that the team accepts
            :param entities_amounts_check: List of EntityAmounts that the team must own in the beginning of transfer
            :param in_blocked: Incoming entites are blocked
            :param out_blocked: Outgoing entities are blocked
        """

        tmp_balance = deepcopy(self.get_balance_complete()) # we do all work on a copy of team's balance
        licence_map = Entity.map_licences(tmp_balance.keys()) # inverse licence mapping

        def get_tmp_balance(entity):
            if entity not in tmp_balance:
                tmp_balance[entity] = Balance(team=self, entity=entity, amount=0, blocked=0)
            return tmp_balance[entity]

        # add/subtracts amounts and check for non-negativity
        def entity_count(ent_am, add):
            balance = get_tmp_balance(ent_am.entity)
            mul = 1 if add else -1
            if (add and in_blocked) or (not add and out_blocked):
                balance.blocked += mul*ent_am.amount
                if balance.blocked < 0:
                    raise ValidationError(str(ent_am.entity)+" is negative")
            else:
                balance.amount += mul*ent_am.amount
                if balance.amount < 0:
                    raise ValidationError(str(ent_am.entity)+" is negative")

        def check_enough(ent_am):
            if get_tmp_balance(ent_am.entity).amount < ent_am.amount:
                raise ValidationError("Not enough %s" % ent_am.entity)

        def licence_check_in(ent_am):
            if ent_am.entity.licence:  # this entity depends on a licence
                licence_bal = get_tmp_balance(ent_am.entity.licence)  # only non-block sum is counted
                this_bal = get_tmp_balance(ent_am.entity)
                if licence_bal.amount == 0 and this_bal.amount > 0:
                    raise ValidationError("No licence for "+str(ent_am.entity))

        def licence_check_out(ent_am):
            if get_tmp_balance(ent_am.entity).amount==0 and ent_am.entity in licence_map: # this entity is a licence and we have none
                for dep in licence_map[ent_am.entity]:
                    dep_bal = get_tmp_balance(dep)
                    if dep_bal.amount > 0:
                        raise ValidationError("%s depends on %s" % (dep, ent_am.entity))

        def commit(ent_am):
            if not pretend:
                get_tmp_balance(ent_am.entity).save()

        # To save items to DB in the correct order, we need to distinguish between licence and dependent items.
        # Here call "licences" all entities that have its licence entry None.
        # Order of checking/saving:
        #  outgoing non-licences
        #  outgoing licences
        #  incoming licences
        #  incoming non-licences

        out_sorted = sorted(entities_amounts_out, key=lambda ent_am: int(ent_am.entity.licence is None))
        in_sorted = sorted(entities_amounts_in, key=lambda ent_am: int(ent_am.entity.licence is not None))

        try:
            for ent_am in entities_amounts_check:
                check_enough(ent_am)

            for ent_am in out_sorted:
                entity_count(ent_am, add=False)
                licence_check_out(ent_am)
                commit(ent_am)

            for ent_am in in_sorted:
                entity_count(ent_am, add=True)
                licence_check_in(ent_am)
                commit(ent_am)

            # save the cache back to the object
            if not pretend:
                self.balance = tmp_balance
            return True
        except ValidationError:
            if pretend:
                return False
            else:
                raise

    def block(self, ent_am, pretend=False):
        return self.transfer(pretend=pretend, entities_amounts_out=ent_am, entities_amounts_in=ent_am, in_blocked=True)

    def unblock(self, ent_am, pretend=False):
        return self.transfer(pretend=pretend, entities_amounts_out=ent_am, entities_amounts_in=ent_am, out_blocked=True)

    def __str__(self):
        return self.name


class Player(models.Model):
    user = models.OneToOneField(User)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        team_str = self.team.name if self.team else "no team"
        return self.user.username+" ("+team_str+")"

class Status(models.Model):
    time = timedelta.TimedeltaField()
    team = models.ForeignKey(Team, null=True, blank=True)
    message = models.TextField()

    def __str__(self):
        return "(%s) %s" % (self.team.name if self.team else "--", self.message)

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

    def total(self):
        return self.amount + self.blocked

    def clean(self):
        """
        Checks whether the team owns a licence for the item;
        When the item itself is a licence, check the count of dependent items is zero

        NOTE: When transferring a group of items, make sure licences are saved first -- otherwise, the following
        constraint fails

        XXX: this is unefficient, consider commenting out in production
        """
        licence = self.entity.licence
        have_licence = False
        try:
            if licence is None or self.team.get_balance(licence).total() > 0:
                have_licence = True
        except KeyError:
            pass
        if self.total() > 0 and not have_licence:
            raise ValidationError("Cannot own %s, licence not present" % self.entity)

        if self.amount==0: # blocked licences don't count
            for entity, balance in self.team.get_balance_complete().items():
                if entity.licence==self.entity and balance.amount > 0:
                    raise ValidationError("Cannot set %s amount to zero, %s depends on it" % (self, entity))

    def __str__(self):
        return "%s: %s (%d + %d blocked) " % (self.team.name, self.entity.name, self.amount, self.blocked)

    class Meta:
        unique_together = ("team", "entity")


class EntityAmount:
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


