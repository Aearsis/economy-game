from django.forms import inlineformset_factory
from django.shortcuts import render, redirect, get_object_or_404

from auctions.forms import *
from auctions.models import WhiteAuction
from ekonomicka.utils import *


def white_list(request):
    return render(request, "auctions/white_list.html", {
        'auctions': WhiteAuction.get_all_active()
    })


@team_required
@game_running_required
def create_auction(request):
    AIFormSet = inlineformset_factory(Auction, AuctionedItem, form=AuctionedItemForm, can_delete=False, extra=1)
    if request.method == "POST":
        form = CreateAuctionForm(request.POST)
        formset = AIFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            data = form.cleaned_data
            data['auctioneditems'] = formset.cleaned_data
            auction = WhiteAuction.create(request.user.player.team, data)
            return redirect(reverse("detail", args={"id": auction.id}))
    else:
        form = CreateAuctionForm()
        formset = AIFormSet()

    return render(request, "auctions/create_auction.html", {
        'form': form,
        'items': formset,
        'empty_item': formset.empty_form,
    })


def detail(request, id):
    auc = get_object_or_404(Auction, pk=id)
    if auc.whiteauction:
        auc = auc.whiteauction
    else:
        auc = auc.blackauction

    winner, current_amount = auc.effective_offer()

    if current_amount is None:
        current_amount = auc.var_min

    return render(request, "auctions/detail.html", {
        'auc': auc,
        'bids': auc.bid_set.all(),
        'winner': winner,
        'sells': auc.auctioneditem_set.filter(amount__gt=0),
        'wants': auc.auctioneditem_set.filter(amount__lt=0),
        'current_amount': current_amount,
    })
