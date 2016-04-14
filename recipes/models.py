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

        for ingredient in Ingredient.objects.filter(recipe=self):
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

    def perform(self, team, pretend=False):
        """
        Apply the recipe for the team.
        :raises ValidationError when there is not enough entities
        """
        (needs, creates, consumes) = self.ingredients()
        with Transaction() as t:
            for q in needs:
                t.needs(team, q.entity, q.amount)
            for q in consumes:
                t.remove(team, q.entity, q.amount)
            team.assert_valid()
            for q in creates:
                t.add(team, q.entity, q.amount)

            if pretend:
                t.clean()
                t.abort()

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
