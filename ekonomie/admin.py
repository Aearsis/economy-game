from django.contrib import admin
from .models import *

admin.site.register(Player)
admin.site.register(Team)

admin.site.register(Entity)

class IngredientsInline(admin.TabularInline):
    model = Ingredient

class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngredientsInline]

admin.site.register(Recipe, RecipeAdmin)


class BidsInline(admin.TabularInline):
    model = Bid
    extra = 0

class AuctionedItemsInline(admin.TabularInline):
    model = AuctionedItem

class AuctionAdmin(admin.ModelAdmin):
    inlines = [BidsInline, AuctionedItemsInline]

admin.site.register(WhiteAuction, AuctionAdmin)
admin.site.register(BlackAuction, AuctionAdmin)

admin.site.register(Status)