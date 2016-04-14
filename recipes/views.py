from django.shortcuts import render

from core.models import Quantity, Balance, Team, InvalidTransaction
from ekonomicka.utils import team_required
from recipes.forms import PerformRecipeForm
from recipes.models import Recipe


# Wrapper class for recipes, its ingredients
class RecipeIngred:
    def __init__(self, recipe: Recipe):
        self.recipe = recipe
        (self.needs, self.creates, self.consumes) = recipe.ingredients()


def index(request):
    recipes = Recipe.objects.all()
    recipes_ingred = []
    for recipe in recipes:
        ri = RecipeIngred(recipe)
        recipes_ingred.append(ri)

    return render(request, "recipes/index.html", { 'recipes_ingred' : recipes_ingred })


@team_required
def detail(request, recipe_id):
    recipe = Recipe.objects.get(id=recipe_id)
    team = request.user.player.team

    recipe_ingred = RecipeIngred(recipe)

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
        'performed':performed
    })
