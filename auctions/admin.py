from django.contrib import admin
from .models import *

class BidsInline(admin.TabularInline):
    model = Bid
    extra = 0

class AuctionedItemsInline(admin.TabularInline):
    model = AuctionedItem

class AuctionAdmin(admin.ModelAdmin):
    inlines = [BidsInline, AuctionedItemsInline]

admin.site.register(WhiteAuction, AuctionAdmin)
admin.site.register(BlackAuction, AuctionAdmin)
