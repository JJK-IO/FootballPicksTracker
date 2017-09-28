from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Team(models.Model):
    name = models.CharField('name', max_length=254, default='', unique=True)
    espn_abbv = models.CharField('espn abbreviation', max_length=8, default='')

    def objectify(self):
        obj = {}
        for f in self._meta.get_fields():
            if not f.is_relation:
                obj[f.name] = getattr(self, f.name)
            else:
                try:
                    obj[f.name] = getattr(self, f.name).objectify()
                except AttributeError:
                    pass
        return obj

    def __str__(self):
        return self.name


class Game(models.Model):
    week = models.IntegerField()
    home_team = models.ForeignKey(Team, related_name='home_team')
    away_team = models.ForeignKey(Team, related_name='away_team')
    datetime = models.DateTimeField()
    season = models.CharField('Season', max_length=8, default='2017')

    def objectify(self):
        obj = {}
        for f in self._meta.get_fields():
            if not f.is_relation:
                obj[f.name] = getattr(self, f.name)
            else:
                try:
                    obj[f.name] = getattr(self, f.name).objectify()
                except AttributeError:
                    pass
        return obj

    def __str__(self):
        return "%s %s %svs%s" % (self.season, self.week, self.home_team.espn_abbv, self.away_team.espn_abbv)


class Pick(models.Model):
    user = models.ForeignKey(User)
    game = models.ForeignKey(Game)
    pick = models.ForeignKey(Team)

    def objectify(self):
        obj = {}
        for f in self._meta.get_fields():
            if not f.is_relation:
                obj[f.name] = getattr(self, f.name)
            else:
                try:
                    obj[f.name] = getattr(self, f.name).objectify()
                except AttributeError:
                    pass
        return obj

    def __str__(self):
        return '%s %s %s' % (self.user.username, self.pick, self.game)


class TieBreaker(models.Model):
    user = models.ForeignKey(User)
    week = models.IntegerField()
    points = models.IntegerField()

    def __str__(self):
        return '%s %s %s' % (self.user.username, self.week, self.points)
