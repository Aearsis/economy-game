from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils.safestring import mark_safe

from auctions.models import WhiteAuction
from core.models import *
from ekonomicka.utils import *
register = template.Library()


def gametime_tag(delta, format, text):
    secs = (Game.to_date(delta) - timezone.now()).total_seconds()
    return mark_safe("<span data-gametime=\"%d\" data-gametime-format=\"%s\">%s</span>" % (secs, format, text))

@register.filter()
def gametime(delta, format_string="%(natural)s;%(natural)s;"):
    before, after, none = format_string.split(";", 3)
    if delta is None:
        return none
    args = {"natural": naturaltime(Game.to_date(delta))}
    if Game.time_passed(delta):
        return gametime_tag(delta, format_string, after % args)
    else:
        return gametime_tag(delta, format_string, before % args)


@register.filter(name='abs')
def absolute(val):
    return abs(val)


@register.filter
def quantity(amount, entity):
    amount = abs(int(amount))
    if amount <= 3:
        return mark_safe(entity_icon(entity) * amount)
    return mark_safe("%s&times;%s" % (amount, entity_icon(entity)))


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

    if team and auction.bid_set.filter(team=team).count() > 0:
        return "danger"

    if auction.is_active():
        return "warning"

    return "default"


@register.filter
def auction_status(auction, team):
    if team:
        if auction is WhiteAuction and auction.seller == team:
            return "Tuto aukci jste vystavili vy."

        winner, _foo = auction.effective_offer
        if winner == team:
            return "Tuto aukci %s." % ("jste vyhráli" if not auction.is_active() else "vyhráváte")

        if auction.bid_set.filter(team=team).count() > 0:
            return "V této aukci jste byli přehozeni."

    return "Této aukce se neúčastníte."


@register.filter
def entity_link_href(entity: Entity, inside):
    return '<a href="%s">%s</a>' % (reverse("entity_detail", args=(entity.id,)), inside)


@register.filter
def entity_link(entity, content=None):
    if content is None:
        content = entity.name
    return mark_safe(entity_link_href(entity, content))


@register.filter
def entity_icon_nolink(entity):
    return mark_safe("<i class=\"eicon eicon-%i\" title=\"%s\"></i>" % (entity.id, entity.name))


@register.filter
def entity_icon(entity):
    return entity_link(entity, entity_icon_nolink(entity))


