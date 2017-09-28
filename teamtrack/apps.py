from django.apps import AppConfig

from logger import Log


class TeamtrackConfig(AppConfig):
    name = 'teamtrack'

    def ready(self):
        Log()
