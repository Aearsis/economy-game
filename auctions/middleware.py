from django.contrib import messages

from auctions.models import Auction, Game


class AuctionCommitMiddleware(object):
    def process_request(self, request):
        if not Game.has_started():
            return
        to_commit = Auction.objects.filter(end__lt=Game.game_time(), commited__exact=False)
        for auc in to_commit:
            messages.add_message(request, messages.DEBUG, "Auction to be commited: %s" % auc)
