from time import timezone

import builtins
from django import template
from django.contrib.humanize.templatetags.humanize import naturaltime

from auctions.models import WhiteAuction
from core.models import *

register = template.Library()


@register.filter
def gametime(delta, format_string="%(natural)s;%(natural)s"):
    args = {"natural": naturaltime(Game.to_date(delta))}
    before, after = format_string.split(";", 2)
    if Game.time_passed(delta):
        return after % args
    else:
        return before % args


@register.filter(name='abs')
def absolute(val):
    return abs(val)


@register.filter
def quantity(amount, entity):
    return "%d %s %s" % (abs(int(amount)), entity.units, entity.name)


@register.filter(is_safe=True)
def amount_control(amount):
    if amount == 0:
        return ""
    if amount < 0:
        return '<span class="label label-danger">%s</span>' % amount
    return '<span class="label label-success">%s</span>' % amount


@register.filter
def auction_class(auction, team):
    if auction is WhiteAuction and auction.seller == team:
        return "primary"

    winner, _foo = auction.effective_offer
    if winner == team:
        return "success"

    if auction.bid_set.filter(team=team).count() > 0:
        return "danger"

    if auction.is_active():
        return "warning"

    return "default"


@register.filter
def auction_status(auction, team):
    if auction is WhiteAuction and auction.seller == team:
        return "Tuto aukci jste vystavili vy."

    winner, _foo = auction.effective_offer
    if winner == team:
        return "Tuto aukci %s." % ("jste vyhráli" if not auction.is_active() else "vyhráváte")

    if auction.bid_set.filter(team=team).count() > 0:
        return "V této aukci jste byli přehozeni."

    return "Této aukce se neúčastníte."
