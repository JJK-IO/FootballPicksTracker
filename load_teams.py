import datetime
import json

import requests
from django.db import IntegrityError

from teamtrack.models import *

api_url = 'http://teamscheduleapi.herokuapp.com/api/v1/NFL/2017'
r = requests.get(api_url)
json_response = json.loads(r.text)

for team in json_response:
    try:
        new_team = Team(
            name=team['full_name'],
            espn_abbv=team['espn_abbv']
        )
        new_team.save()
    except IntegrityError:
        print("team:%s already exists" % team['espn_abbv'])

for team in json_response:
    for game in team['games']:
        if game['week'] not in ['P1', 'P2', 'P3', 'P4']:
            if game['home'] is not None and game['opponent'] is not None:
                if game['home']:
                    home_team = Team.objects.get(name=team['full_name'])
                    away_team = Team.objects.get(name=game['opponent'])
                else:
                    away_team = Team.objects.get(name=team['full_name'])
                    home_team = Team.objects.get(name=game['opponent'])
                week = int(game['week'])
                existing_games = Game.objects.filter(
                    week=week,
                    home_team=home_team,
                    away_team=away_team,
                    datetime=game['date'],
                    # "2017-08-20T00:00:00.000-04:00"
                    season=game['season']
                )
                if len(existing_games) == 0:
                    new_game = Game(
                        week=week,
                        home_team=home_team,
                        away_team=away_team,
                        datetime=game['date'],
                        season=game['season']
                    )
                    new_game.save()
                else:
                    print("%s already exists" % existing_games[0])
        else:
            print("Skipping Preseason")