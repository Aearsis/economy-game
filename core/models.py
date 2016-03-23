from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import timedelta
from django.core.exceptions import ValidationError

# Single row to hold game state
class Game(models.Model):
    started = models.DateTimeField(null=True, blank=True)

    def has_started(self):
        return self.started is not None

    def time_passed(self, delta):
        return self.started + delta >= timezone.now()

    def game_time(self):
        return timezone.now() - self.started

class Team(models.Model):
    name = models.CharField(max_length=256, unique=True)
    visible = models.BooleanField(default=False)

    def balance(self):
        """
        Returns team's balance as a dictionary { entity:balance }
        :rtype Dict[Entity, Balance]
        """
        bal = Balance.objects.filter(team=self)
        return { balance.entity:balance for balance in bal }

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
        """
        licence = self.entity.licence
        team_balance = self.team.balance()
        have_licence = False
        try:
            if licence is None or team_balance[licence].total() > 0:
                have_licence = True
        except KeyError:
            pass
        if self.total() > 0 and not have_licence:
            raise ValidationError("Cannot own %s, licence not present" % self.entity)

        if self.amount==0: # blocked licences don't count
            for entity, balance in team_balance.items():
                if entity.licence==self.entity and balance.amount > 0:
                    raise ValidationError("Cannot set %s amount to zero, %s depends on it" % (self, entity))



    def __str__(self):
        return "%s: %s (%d + %d blocked) " % (self.team.name, self.entity.name, self.amount, self.blocked)

    class Meta:
        unique_together = ("team", "entity")

