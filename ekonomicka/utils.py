from django.utils import timezone

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.views import redirect_to_login
from django.core.urlresolvers import reverse
from django import template

from core.models import Game


def player_required(view_func):
    """
    Decorator that ensures logged user is a player

    """
    player_decorator = user_passes_test(
        lambda u: hasattr(u, 'player'),
    )
    return player_decorator(view_func)


def team_required(view_func):
    """
    Decorator that ensures logged player has its own team -> request.team != None.
    User must be logged in (if not, redirect to login_url), and have a team (if not, redirect to core.team)

    """
    team_decorator = user_passes_test(
        lambda u: u.player.team is not None,
        login_url='/team/create/'
    )
    return player_required(team_decorator(view_func))


def game_running_required(view_func):
    """
    Decorator that ensures the current game is running
    """

    def wrapped_view(request, *args, **kwargs):
        if Game.is_running():
            return view_func(request, *args, **kwargs)

        return redirect_to_login(request.build_absolute_uri(), reverse("wait"))

    return wrapped_view


def naturaljoin(items, sep=", ", last=" a ", empty=""):
    if not isinstance(items, list):
        items = list(items)
    if len(items) == 0:
        return empty
    if len(items) == 1:
        return str(items[0])

    return "%s%s%s" % (sep.join(items[:-1]), last, items[-1])