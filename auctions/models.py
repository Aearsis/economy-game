from core.models import *
import timedelta
import datetime


class Auction(models.Model):
    begin = timedelta.TimedeltaField()
    end = timedelta.TimedeltaField()

    var_entity = models.ForeignKey(Entity)
    var_min = models.IntegerField()
    var_step = models.PositiveIntegerField(default=1)

    commited = models.BooleanField(default=False)
    buyer = models.ForeignKey(Team, null=True)

    def highest_offer(self):
        """
        Returns the effective (visible) offer or None if there was no offer yet
        """
        pass

    def __str__(self):
        return "Prostě aukce. To je bug."


class WhiteAuction(Auction):
    seller = models.ForeignKey(Team)
    description = models.TextField(max_length=256, null=True)

    def __str__(self):
        return "Aukce od uživatele %s" % self.seller.name

    @staticmethod
    def active():
        return WhiteAuction.objects.filter(end__gt=timezone.now())

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
        return "%s (%d)%s%s" % (
        self.entity.name, self.amount, " skrytě" if not self.visible else "", " fake" if not self.will_sell else "")

    class Meta:
        unique_together = ("auction", "entity")


class Bid(models.Model):
    auction = models.ForeignKey(Auction)
    team = models.ForeignKey(Team)
    amount = models.PositiveIntegerField()

    class Meta:
        unique_together = ("auction", "team")
