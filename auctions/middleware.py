from auctions.models import *


class AuctionCommitMiddleware(object):
    def process_request(self, request):
        if not Game.has_started():
            return

        to_commit = list(WhiteAuction.objects.filter(end__lt=Game.game_time(), commited__exact=False))
        to_commit += list(BlackAuction.objects.filter(end__lt=Game.game_time(), commited__exact=False))
        for auc in to_commit:
            auc.commit()
