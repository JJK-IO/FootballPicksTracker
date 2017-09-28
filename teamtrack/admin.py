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


admin.site.register(models.Team, TeamAdmin)
admin.site.register(models.Game, GameAdmin)
admin.site.register(models.Pick)
admin.site.register(models.TieBreaker)