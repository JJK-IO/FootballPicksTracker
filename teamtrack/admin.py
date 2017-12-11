from django.contrib import admin

# Register your models here.
from teamtrack import models


class TeamAdmin(admin.ModelAdmin):
    search_fields = [
        "name",
        "espn_abbv"
    ]


class GameAdmin(admin.ModelAdmin):
    search_fields = [
        "week",
        "home_team__name",
        "home_team__espn_abbv",
        "away_team__name",
        "away_team__espn_abbv",
        "season"
    ]


class PickAdmin(admin.ModelAdmin):
    search_fields = [
        "user__username"
    ]


admin.site.register(models.Team, TeamAdmin)
admin.site.register(models.Game, GameAdmin)
admin.site.register(models.Pick, PickAdmin)
admin.site.register(models.TieBreaker)
