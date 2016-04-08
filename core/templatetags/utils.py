from time import timezone

import builtins
from django import template
from django.contrib.humanize.templatetags.humanize import naturaltime

from core.models import *

register = template.Library()


@register.filter
def gametime(delta):
    return naturaltime(Game.to_date(delta))


@register.filter(name='abs')
def absolute(val):
    return abs(val)


@register.filter
def quantity(amount, entity):
    return "%d %s %s" % (abs(int(amount)), entity.units, entity.name)
