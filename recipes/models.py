from django.db import models
from core.models import *

class Recipe(models.Model):
    name = models.TextField()
    description = models.TextField()


    def perform(self, team):
        """
        Apply the recipe for the team. Throws ValidationError when there is not enough entities.
        :param team: Team
        """
        pass

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

