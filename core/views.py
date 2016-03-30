from django.shortcuts import render, redirect
from django.forms import ModelForm
from core.models import *
from ekonomicka.utils import *


@team_required
def team(request):
    return render(request, "core/team.html", { 'team' : request.user.player.team })

class TeamForm(ModelForm):
    class Meta:
        model = Team
        fields = [ 'name', 'members' ]

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