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
    name = models.TextField(max_length=256, unique=True)
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
    name = models.TextField()
    units = models.TextField(blank=True)
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


class Recipe(models.Model):
    name = models.TextField()
    description = models.TextField()

    def __str__(self):
        return "%s: %s" % (self.name, self.description)

class Ingredient(models.Model):
    CONSUME = 0,
    NEED = 1,
    CREATE = 2,
    TYPES = (
        (CONSUME, "Consumes"),
        (NEED, "Needs"),
        (CREATE, "Creates"),
    )
    recipe = models.ForeignKey(Recipe)
    entity = models.ForeignKey(Entity)
    type = models.PositiveSmallIntegerField(choices=TYPES)
    amount = models.IntegerField()

    class Meta:
        unique_together = ("recipe", "entity", "type")


class Auction(models.Model):
    begin = timedelta.TimedeltaField()
    end = timedelta.TimedeltaField()
    description = models.TextField(max_length=256)
    wants = models.ForeignKey(Entity)
    minimum = models.PositiveIntegerField()
    bid_step = models.PositiveIntegerField()
    transaction_made = models.BooleanField(default=False)

    def __str__(self):
        return "Prostě aukce. To je bug."

class WhiteAuction(Auction):
    seller = models.ForeignKey(Team)

    def __str__(self):
        return "Aukce od uživatele %s" % self.seller.name

    class Meta:
        verbose_name_plural = "Auctions"

class BlackAuction(Auction):
    seller_name = models.TextField()
    status_text = models.TextField()

    def __str__(self):
        return "Černý trh: %s" % self.status_text

    class Meta:
        verbose_name_plural = "Black market offers"

class AuctionedItem(models.Model):
    auction = models.ForeignKey(Auction)
    entity = models.ForeignKey(Entity)
    amount = models.PositiveIntegerField()
    visible = models.BooleanField()
    will_sell = models.BooleanField()

    def __str__(self):
        return "%s (%d)%s%s" % (self.entity.name, self.amount, " skrytě" if not self.visible else "", " fake" if not self.will_sell else "")

    class Meta:
        unique_together = ("auction", "entity")

class Bid(models.Model):
    auction = models.ForeignKey(Auction)
    team = models.ForeignKey(Team)
    amount = models.PositiveIntegerField()

    class Meta:
        unique_together = ("auction", "team")