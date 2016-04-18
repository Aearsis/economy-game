from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from .forms import *
from core.models import *
from ekonomicka.utils import *
from recipes.models import *
from auctions.models import *


@team_required
def team(request):
    return render(request, "core/team.html", {
        'team': request.team,
        'balance': request.team.balance_set.all()
    })


@player_required
def create_team(request, next="/team"):
    if request.team is not None:
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

    return render(request, "core/create_team.html", {'form': form})


def messages(request):
    data = Status.visible()
    return render(request, 'dashboard/messages.html', {'statuses': data[0], 'refreshed': data[1]})


def messages_standalone(request):
    data = Status.visible()
    return render(request, 'dashboard/messages.html', {'statuses': data[0], 'refreshed': data[1]})


def inventory(request):
    entities = Entity.objects.order_by("name")
    teams = Team.objects.order_by("name")
    table = [[team.get_balance(entity) for team in teams] for entity in entities]

    table_filtered = []
    for row in table:
        owned = False
        for bal in row:
            if bal.amount > 0:
                owned = True
        if owned:
            table_filtered.append(row)

    return render(request, 'dashboard/inventory.html', {
        'teams': teams,
        'table': table_filtered,
        'team': request.team,
    })


@permission_required("control_game")
def control(request):
    return render(request, 'core/control.html', {
        'game': Game,
        'balances': Balance.objects.order_by('team', 'entity').all()
    })


@permission_required("control_game")
def control_start(request):
    Game.start_now()
    return redirect(reverse("control"))


@team_required
def wait_to_start(request):
    if (Game.is_running()):
        if 'next' in request.GET:
            return redirect(request.GET['next'])
        else:
            return redirect(reverse("team"))
    else:
        return render(request, "core/wait.html", {
            'game': Game.the_row()
        })


def entity_detail(request, entity_id):
    entity = Entity.objects.get(id=entity_id)
    licences = entity.licences.all()

    # owners of the entity
    balances = Balance.objects.filter(entity=entity, amount__gt=0)

    # what recipes it is used in
    ingredients = Ingredient.objects.filter(entity=entity)
    recipes = {ingr.recipe for ingr in ingredients}

    # auctions
    items = AuctionedItem.objects.filter(entity=entity)
    auctions_var = Auction.objects.filter(var_entity=entity)
    auctions_set = {item.auction for item in items}.union({auction for auction in auctions_var})

    auctions = []
    for auction in auctions_set:
        if auction.is_active():
            auctions.append(auction)
    auctions.sort(key=lambda auc: auction.concrete_auction.is_white())

    return render(request, "core/entity_detail.html", {
        'entity': entity,
        'balances': balances,
        'licences': licences,
        'recipes': recipes,
        'auctions': auctions,
    })


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


def entity_list(request):
    return render(request, "core/entity_list.html", {
        'entities': Entity.objects.order_by('name').all()
    })
