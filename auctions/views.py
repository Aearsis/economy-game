from django.shortcuts import render

from auctions.models import WhiteAuction


def white_list(request):
    return render(request, "auctions/white_list.html", {
        'auctions' : WhiteAuction.active()
    })