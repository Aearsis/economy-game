from django.contrib import admin
from .models import *

class IngredientsInline(admin.TabularInline):
    model = Ingredient

class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngredientsInline]

admin.site.register(Recipe, RecipeAdmin)