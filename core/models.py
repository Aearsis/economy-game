from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import timedelta

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

    def __str__(self):
        return self.name

class Player(models.Model):
    user = models.OneToOneField(User)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

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
    amount = models.PositiveIntegerField()
    blocked = models.PositiveIntegerField()

    def __str__(self):
        return "%s: %s (%d + %d blocked) " % (self.team.name, self.entity.name, self.amount, self.blocked)

    class Meta:
        unique_together = ("team", "entity")

