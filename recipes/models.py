from django.db import models
from core.models import *

class Recipe(models.Model):
    name = models.TextField()
    description = models.TextField()

    def ingredients(self):
        """
        Transforms ingredients to lists of Quantities
        """
        needs = []
        creates = []
        consumes = []

        ingredients = Ingredient.objects.filter(recipe=self)
        for ingredient in ingredients:
            arr = []
            if ingredient.type == Ingredient.NEED:
                arr = needs
            elif ingredient.type == Ingredient.CREATE:
                arr = creates
            elif ingredient.type == Ingredient.CONSUME:
                arr = consumes
            else:
                assert False

            arr.append(Quantity(ingredient.entity, ingredient.amount))

        return (needs, creates, consumes)

    def perform(self, team):
        """
        Apply the recipe for the team.
        :raises ValidationError when there is not enough entities
        """

        (needs, creates, consumes) = self.ingredients()

        team.check_balance(needs)

        t = Transaction(team)
        t.add(creates)
        t.remove(consumes)
        t.commit()

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

