from core.models import *
import timedelta
import datetime


class Auction(models.Model):
    begin = timedelta.TimedeltaField()
    end = timedelta.TimedeltaField()
    description = models.TextField(max_length=256, null=True)
    wants = models.ForeignKey(Entity)
    minimum = models.PositiveIntegerField()
    bid_step = models.PositiveIntegerField(default=1)
    transaction_made = models.BooleanField(default=False)

    def highest_offer(self):
        """
        Returns the effective (visible) offer or None if there was no offer yet
        """
        pass

    def __str__(self):
        return "Prostě aukce. To je bug."


class WhiteAuction(Auction):
    seller = models.ForeignKey(Team)

    @staticmethod
    @transaction.atomic
    def create(seller: Team, end: datetime.timedelta, wants: Quantity, offers: List[Quantity],
               bid_step: int):
        """
        Checks for items and creates a standard white auction.
        :raises ValidationError on failure
        :rtype WhiteAuction
        """

        # block offered items and licence of wanted item
        seller.block(offers)
        if wants.entity.licence:
            seller.block_auction(wants.entity.licence)
        ### XXX: breaks balance cache when it fails

        auction = WhiteAuction()
        auction.begin = Game.the_row().to_delta(timezone.now())
        auction.end = end
        auction.wants = wants.entity
        auction.minimum = wants.amount
        auction.bid_step = bid_step
        auction.seller = seller
        auction.save()

        for offer in offers:
            item = AuctionedItem(auction=auction, entity=offer.entity, amount=offer.amount, visible=True, will_sell=True)
            item.save()

        return auction

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