from auctions.models import *


class AuctionCommitMiddleware(object):
    def process_request(self, request):
        if not Game.has_started():
            return

        to_commit = Auction.objects.filter(end__lt=Game.game_time(), commited__exact=False).all()
        for auc in to_commit:
            auc.concrete_auction.commit()
