from django.db import models
from core.models import *

class Recipe(models.Model):
    name = models.TextField()
    description = models.TextField()

    def ingredients(self):
        needs = []
        creates = []
        consumes = []

        ingredients = Ingredient.objects.filter()
        for ingredient in ingredients:
            arr = []
            if ingredient.type==Ingredient.NEED:
                arr = needs
            elif ingredient.type==Ingredient.CREATE:
                arr = creates
            elif ingredient.type==Ingredient.CONSUME:
                arr = consumes
            else:
                assert False

            arr.append(EntityAmount(ingredient.entity, ingredient.amount))

        return (needs, creates, consumes)

    def perform(self, team):
        """
        Apply the recipe for the team. Throws ValidationError when there is not enough entities.
        :param team: Team
        """

        (needs, creates, consumes) = self.ingredients()
        ingredients = Ingredient.objects.filter()
        team.transfer(pretend=False, entities_amounts_in=creates, entities_amounts_out=consumes, entities_amounts_check=needs)

    def __str__(self):
        return "%s: %s" % (self.name, self.description)

class Ingredient(models.Model):
    CONSUME = 0
    NEED = 1
    CREATE = 2
    TYPES = (
        (CONSUME, "Consumes"),
        (NEED, "Needs"),
        (CREATE, "Creates"),
    )
    recipe = models.ForeignKey(Recipe)
    entity = models.ForeignKey(Entity)
    type = models.PositiveSmallIntegerField(choices=TYPES)
    amount = models.IntegerField()

    class Meta:
        unique_together = ("recipe", "entity", "type")

