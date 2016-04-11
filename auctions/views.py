from django.contrib import messages
from django.forms import inlineformset_factory
from django.http import Http404
from django.shortcuts import render, redirect

from auctions.forms import *
from auctions.models import WhiteAuction
from ekonomicka.utils import *


@game_running_required
def white_list(request):
    return render(request, "auctions/white_list.html", {
        'auctions': WhiteAuction.objects.filter(begin__lte=Game.game_time())
                  .order_by('-end').all()
    })


@game_running_required
def black_market(request):
    return render(request, "auctions/black_market.html", {
        'auctions': BlackAuction.objects.filter(begin__lte=Game.game_time())
                  .order_by('-end', '-begin').all()
    })


@team_required
@game_running_required
def create_auction(request):
    AIFormSet = inlineformset_factory(Auction, AuctionedItem, form=AuctionedItemForm, can_delete=False, extra=1)
    if request.method == "POST":
        form = CreateAuctionForm(request.POST)
        formset = AIFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            try:
                data = form.cleaned_data
                data['auctioneditems'] = formset.cleaned_data
                auction = WhiteAuction.create(request.team, data)
                messages.add_message(request, messages.SUCCESS, "Aukce byla vytvořena.")
                return redirect(reverse("detail", args=(auction.id,)))
            except InvalidTransaction as e:
                form.add_error(None, str(e))
    else:
        form = CreateAuctionForm()
        formset = AIFormSet()

    return render(request, "auctions/create_auction.html", {
        'form': form,
        'items': formset,
        'empty_item': formset.empty_form,
    })


def get_active_auction(pk):
    try:
        auc = Auction.objects.get(pk=pk)
        if not Game.time_passed(auc.begin):
            raise 1
    except:
        raise Http404("Tato aukce neexistuje.")
    if auc.whiteauction:
        auc = auc.whiteauction
    else:
        auc = auc.blackauction
    return auc


@team_required
def place_bid(request, auc: Auction, bf: BidForm):
    team = request.team
    try:
        auc.place_bid(team, bf.cleaned_data['bid'] * bf.cleaned_data['coef'])
        winner, offer = auc.effective_offer
        if winner == team:
            messages.add_message(request, messages.SUCCESS, "Výborně! Nyní vyhráváte tuto aukci.")
        else:
            messages.add_message(request, messages.WARNING, "Bohužel, byli jste přehozeni. Zkuste nabídnout více!")

        return redirect("detail", auc.id)
    except AuctionException as e:
        bf.add_error('bid', str(e))


@game_running_required
def detail(request, auction):
    auc = get_active_auction(auction)
    winner, current_amount = auc.effective_offer

    if winner is None:
        current_amount = auc.var_min

    minimum = auc.minimum_bid()

    if request.method == 'POST':
        bf = BidForm(request.POST)
        if bf.is_valid():
            r = place_bid(request, auc, bf)
            if r is not None:
                return r
    else:
        bf = BidForm(initial={"bid": abs(minimum), "coef": 1 if minimum > 0 else -1})

    return render(request, "auctions/detail.html", {
        'auc': auc,
        'is_mine': auc is WhiteAuction and auc.seller == request.team,
        'bids': auc.bid_set.all(),
        'winner': winner,
        'form': bf,
        'current_amount': current_amount,
        'minimum': minimum
    })
