from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from .forms import *
from core.models import *
from ekonomicka.utils import *

@team_required
def team(request):
    return render(request, "core/team.html", {
        'team' : request.user.player.team,
        'inventory' : Balance.objects.filter(team = request.user.player.team).order_by('entity__name'),
    })

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
    entities = Entity.objects.order_by("name")
    teams = Team.objects.order_by("name")
    table = [[team.get_balance(entity) for team in teams] for entity in entities]
    return render(request, 'dashboard/index.html', {
        'statuses' : data[0],
        'refreshed' : data[1],
        'teams' : teams,
        'table' : table,
    })


@permission_required("control_game")
def control(request):
    return render(request, 'core/control.html', {
        'game' : Game,
    })

@permission_required("control_game")
def control_start(request):
    Game.start_now()
    return redirect(reverse("control"))

@team_required
def wait_to_start(request):
    if (Game.has_started()):
        if 'next' in request.GET:
            return redirect(request.GET['next'])
        else:
            return redirect(reverse("team"))
    else:
        return render(request, "core/wait.html")

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