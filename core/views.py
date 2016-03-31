from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from .forms import *
from core.models import *
from ekonomicka.utils import *

@team_required
def team(request):
    return render(request, "core/team.html", { 'team' : request.user.player.team })

@player_required
def create_team(request, next = "/team"):
    if (request.user.player.team is not None):
        return redirect(next)

    if (request.method == 'POST'):
        form = TeamForm(request.POST)
        if form.is_valid():
            pl = request.user.player
            pl.team = form.save()
            pl.save()
            return redirect(next)
    else:
        form = TeamForm()

    return render(request, "core/create_team.html", { 'form': form })


def dashboard(request):
    data = Status.visible()
    return render(request, 'dashboard/index.html', { 'data' : data[0], 'refreshed' : data[1] })


@permission_required("control_game")
def control(request):
    return render(request, 'core/control.html', {
        'game' : Game,
    })

@permission_required("control_game")
def control_start(request):
    Game.start_now()
    return redirect(reverse("control"))


def router(request):
    """
    Hacky view that redirects based on current privileges.
    """
    if not request.user.is_authenticated():
        return redirect(reverse("login"))

    if request.user.has_perm('control_game'):
        return redirect(reverse("control"))

    groups = request.user.groups
    if groups.filter(name='Team').exists():
        return redirect(reverse("team"))

    if groups.filter(name='Dashboard').exists():
        return redirect(reverse("dashboard"))

    return redirect(reverse("team"))