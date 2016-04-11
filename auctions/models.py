from core.models import *
import timedelta
import datetime


class Auction(models.Model):
    begin = timedelta.TimedeltaField()
    end = timedelta.TimedeltaField()

    # buyer gives seller the highest possible amount of var_entity.
    # positive: buyer --> seller
    # negative: buyer <-- seller
    var_entity = models.ForeignKey(Entity)
    var_min = models.IntegerField()
    var_step = models.PositiveIntegerField(default=1)

    commited = models.BooleanField(default=False)
    buyer = models.ForeignKey(Team, null=True, blank=True)

    def is_active(self):
        return not Game.time_passed(self.end) and Game.time_passed(self.begin)

    @property
    def ordered_bids(self):
        return self.bid_set.order_by("-amount", "placed")

    @property
    def effective_offer(self):
        """
        Winning offer according to auction rules
        Returns pair (highest bidder, amount).
        """
        bids = self.ordered_bids
        count = len(bids)
        if count == 0:
            return None, 0
        elif count == 1:
            return bids[0].team, self.var_min
        else:
            return bids[0].team, min(bids[1].amount + self.var_step, bids[0].amount)

    @property
    def highest_bid(self):
        """
        If not None, this is the only bid that is blocked.
        """
        return self.ordered_bids.first()

    def __str__(self):
        return "Prostě aukce. To je bug."

    @transaction.atomic
    def place_bid(self, team, amount):
        """
        Places bid and ensures the highest and only the highest bid is blocked.
        Also checks placing bid is possible.
        """
        if not self.is_active():
            raise AuctionException("Aukce už skončila.")

        eff_bidder, eff_amount = self.effective_offer
        if eff_amount is not None:
            min_amount = eff_amount + self.var_step
            if min_amount >= amount:
                raise AuctionException("Musíš nabídnout alespoň %i." % min_amount)

        highest_bid = self.highest_bid

        team_bid = self.bid_set.get_or_create(team=team)
        team_bid.amount = amount
        team_bid.placed = Game.game_time()

        with Transaction() as t:
            if highest_bid is not None:
                highest_bid.unblock(t)

            if highest_bid is None or highest_bid.amount < team_bid.amount:
                highest_bid = team_bid

            highest_bid.block(t)

        team_bid.save()

    def _commit_seller(self, t: Transaction, var_amount):
        """
        Add entities bought, remove sold (including variable in var_amount).
        Remember to unblock everything.
        """
        pass # generic auction has no seller

    def _commit_buyer(self, t: Transaction, var_amount):
        """
        Add entities bought, remove sold (including variable in var_amount).
        Remember to unblock everything bidded.
        """
        t.remove(self.buyer, self.var_entity, var_amount)
        for item in self.auctioneditem_set:
            t.add(self.buyer, item.entity, item.amount)

    @transaction.atomic
    def commit(self):
        if self.commited:
            return

        self.commited = True

        bidder, amount = self.effective_offer
        self.buyer = bidder

        highest_bid = self.highest_bid

        with Transaction() as t:
            if highest_bid is not None:
                highest_bid.unblock(t)
            self._commit_seller(t, amount)
            if bidder is not None:
                self._commit_buyer(t, amount)

        # add status
        self.save()

    @property
    def sells(self):
        return self.auctioneditem_set.filter(amount__gt=0)

    @property
    def wants(self):
        return self.auctioneditem_set.filter(amount__lt=0)


class AuctionException(Exception):
    pass


class WhiteAuction(Auction):
    seller = models.ForeignKey(Team)
    description = models.TextField(max_length=256, null=True)

    def __str__(self):
        return "Aukce od uživatele %s" % self.seller.name

    @staticmethod
    def get_all_active():
        now = Game.game_time()
        if now is None:
            return []
        return WhiteAuction.objects.filter(end__gt=now, begin__lt=now)

    def place_bid(self, team, amount):
        if team == self.seller:
            raise AuctionException("Nemůžeš přihazovat k vlastní aukci.")

        return super().place_bid(team, amount)

    def _commit_seller(self, t: Transaction, var_amount):
        if self.var_min < 0:
            t.unblock(self.seller, self.var_entity, -self.var_min)
        else:
            t.unexpect(self.seller, self.var_entity, self.var_min)

        for ai in self.sells:
            t.unblock(self.seller, ai.entity, ai.amount)

        for ai in self.wants:
            t.unexpect(self.seller, ai.entity, -ai.amount)

        if self.buyer is None:
            return

        t.add(self.seller, self.var_entity, var_amount)

        for ai in self.auctioneditem_set:
            t.remove(self.seller, ai.entity, ai.amount)

    @staticmethod
    @transaction.atomic
    def create(team: Team, data):
        auc = WhiteAuction()
        auc.begin = Game.game_time()
        auc.description = data['description']
        auc.end = auc.begin + datetime.timedelta(seconds=int(data['timespan']))
        auc.var_entity = data['var_entity']
        auc.var_min = data['var_min'] * int(data['var_direction'])
        auc.var_step = data['var_step']
        auc.seller = team
        auc.save()

        with Transaction() as t:
            if auc.var_min < 0:
                t.block(team, auc.var_entity, -auc.var_min)
            else:
                t.expect(team, auc.var_entity, auc.var_min)

            for item in data['auctioneditems']:
                ai = AuctionedItem(auction=auc, entity=item['entity'],
                                   amount=item['amount'] * int(item['coef']))
                if ai.amount > 0:
                    t.block(team, ai.entity, ai.amount)
                else:
                    t.expect(team, ai.entity, -ai.amount)
                ai.save()

        return auc

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
    """
    Something that seller gives to buyer.
    positive: seller --> buyer,
    negative: seller <-- buyer
    """
    auction = models.ForeignKey(Auction)
    entity = models.ForeignKey(Entity)
    amount = models.IntegerField()
    visible = models.BooleanField(default=True)
    will_sell = models.BooleanField(default=True)

    def __str__(self):
        return "%s (%d)%s%s" % (
            self.entity.name, self.amount, " skrytě" if not self.visible else "", " fake" if not self.will_sell else "")

    def block_expect(self, t: Transaction, bidder: Team, coef=1):
        """
        Blocks/expects the item for the highest bidder.
        """
        if self.amount < 0:
            t.block(bidder, self.entity, -self.amount * coef)
        else:
            t.expect(bidder, self.entity, self.amount * coef)

    def unblock(self, t: Transaction, bidder: Team):
        self.block(t, bidder, coef=-1)

    class Meta:
        unique_together = ("auction", "entity")


class Bid(models.Model):
    auction = models.ForeignKey(Auction)
    team = models.ForeignKey(Team)
    amount = models.PositiveIntegerField()
    placed = timedelta.TimedeltaField()

    def block(self, t: Transaction, coef=1):
        auc = self.auction
        if self.amount > 0:
            t.block(self.team, auc.var_entity, self.amount * coef)
        else:
            t.expect(self.team, auc.var_entity, -self.amount * coef)
        for item in auc.auctioneditem_set:
            item.block_expect(t, self.team, coef)

    def unblock(self, t: Transaction):
        self.block(t, coef=-1)

    class Meta:
        unique_together = ("auction", "team")
