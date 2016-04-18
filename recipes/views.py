from django.shortcuts import render

from core.models import Quantity, Balance, Team, InvalidTransaction
from ekonomicka.utils import team_required
from recipes.forms import PerformRecipeForm
from recipes.models import Recipe


# Wrapper class for recipes, its ingredients
class RecipeIngred:
    def __init__(self, recipe: Recipe, team:Team):
        self.recipe = recipe
        self.can_perform = recipe.can_perform(team)
        (self.needs, self.creates, self.consumes) = recipe.ingredients()


@team_required
def index(request):
    recipes = [ recipe for recipe in Recipe.objects.all() ]
    team = request.user.player.team

    recipes_ingred = []
    for recipe in recipes:
        ri = RecipeIngred(recipe, team)
        recipes_ingred.append(ri)

    recipes_ingred.sort(key=lambda recipe_ingred: not recipe_ingred.can_perform)

    return render(request, "recipes/index.html", { 'recipes_ingred' : recipes_ingred })


@team_required
def detail(request, recipe_id):
    recipe = Recipe.objects.get(id=recipe_id)
    team = request.user.player.team

    recipe_ingred = RecipeIngred(recipe, team)

    performed = False
    if request.method=="POST":
        recipe.perform(team)
        performed = True

    errors = ""
    is_possible = False
    try:
        recipe.perform(team, pretend=True)
        is_possible = True
    except InvalidTransaction as e:
        errors = str(e)




    return render(request, "recipes/detail.html", {
        'recipe_ingred':recipe_ingred,
        'is_possible':is_possible,
        'errors':errors,
        'form':PerformRecipeForm(),
        'performed':performed,
        'balance': request.team.balance_set.all(),
    })
