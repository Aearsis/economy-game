from django.db import models
from core.models import *
import timedelta

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
    seller_name = models.CharField(max_length=128)
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