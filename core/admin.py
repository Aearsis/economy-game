from django.contrib import admin
from .models import *

class BalancesInline(admin.TabularInline):
    model = Balance

class TeamAdmin(admin.ModelAdmin):
    inlines = [ BalancesInline ]

admin.site.register(Player)
admin.site.register(Team, TeamAdmin)

admin.site.register(Entity)

admin.site.register(Status)
