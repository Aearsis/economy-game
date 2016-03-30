from django.contrib.auth.decorators import user_passes_test


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
    Decorator that ensures logged player has its own team -> request.user.player.team != None.
    User must be logged in (if not, redirect to login_url), and have a team (if not, redirect to core.team)

    """
    team_decorator = user_passes_test(
        lambda u: u.player.team is not None,
        login_url = '/team/create/'
    )
    return player_required(team_decorator(view_func))
