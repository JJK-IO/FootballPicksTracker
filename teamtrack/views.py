# Create your views here.
import json

from django.contrib import auth
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.context_processors import csrf
from django.urls import reverse
from django.utils import timezone
from django.views import View

from logger import Log
from teamtrack.models import Game, Team, Pick, TieBreaker


class IndexView(View):
    def get(self, request):
        latest_week = Game.objects.all().order_by('-week')[0].week
        all_games = Game.objects.all().order_by('week')
        game_weeks = []
        for week in range(1, latest_week):
            first_game = Game.objects.filter(week=week).order_by('datetime')[0]
            pick_allowed = True
            if timezone.now() > first_game.datetime:
                pick_allowed = False
            user_picked = False
            if request.user.is_authenticated():
                if len(Pick.objects.filter(user=request.user, game=first_game)) != 0:
                    user_picked = True
            game_weeks.append({'week': week, 'open': pick_allowed, 'picked': user_picked})

        return render(request, 'teamtrack/index.html', {
            'games': all_games,
            'game_weeks': game_weeks,
            'this_week': get_closest_game_by_date(timezone.now()).week
        })


class WeekPickView(View):
    def get(self, request, week):
        games = Game.objects.filter(week=week).order_by('datetime')
        game_data = []

        for game in games:
            try:
                pick = Pick.objects.get(game=game, user=request.user).pick
            except Pick.DoesNotExist:
                pick = None
            game_data.append({
                'game': game,
                'user_pick': pick
            })

        try:
            monday_points = TieBreaker.objects.get(week=week, user=request.user).points
        except TieBreaker.DoesNotExist:
            monday_points = ""

        kwargs = {
            'game_data': game_data,
            'monday_points': monday_points,
            'this_week': get_closest_game_by_date(timezone.now()).week,
            'disabled': False
        }

        if timezone.now() > games[0].datetime:
            kwargs['disabled'] = True

        return render(request, 'teamtrack/week.html', kwargs)

    def post(self, request, week):
        json_data = json.loads(request.body.decode("utf-8"))
        errors = []
        errors_game_id = []
        first_game = Game.objects.filter(week=week).order_by('datetime')[0]
        if 'choices' in json_data:
            for choice in json_data['choices']:
                relevant_game = Game.objects.get(id=choice['game'])
                try:
                    user_pick = Pick.objects.get(
                        user=request.user,
                        game=relevant_game
                    )
                    if timezone.now() < first_game.datetime:
                        user_pick.pick = Team.objects.get(name=choice['winner'])
                        user_pick.save()
                    else:
                        if user_pick.pick != Team.objects.get(name=choice['winner']):
                            errors.append(
                                'Cannot update %s vs %s game after the first game of week has already started.' % (
                                    relevant_game.home_team, relevant_game.away_team
                                ))
                            errors_game_id.append(relevant_game.id)
                except Pick.DoesNotExist:
                    if timezone.now() < first_game.datetime:
                        new_pick = Pick(
                            user=request.user,
                            game=relevant_game,
                            pick=Team.objects.get(name=choice['winner'])
                        )
                        new_pick.save()
                    else:
                        errors.append(
                            'Cannot update %s vs %s game after the first game of week has already started.' % (
                                relevant_game.home_team, relevant_game.away_team
                            ))
                        errors_game_id.append(relevant_game.id)
        if 'monday_points' in json_data:
            if timezone.now() < first_game.datetime:
                try:
                    tie_break = TieBreaker.objects.get(
                        user=request.user,
                        week=week
                    )
                    tie_break.points = int(json_data['monday_points'])
                    tie_break.save()
                except TieBreaker.DoesNotExist:
                    new_tie_breaker = TieBreaker(
                        user=request.user,
                        week=week,
                        points=int(json_data['monday_points'])
                    )
                    new_tie_breaker.save()
            else:
                errors.append(
                    'Cannot update monday game tie breaker points after the first game of week has already started.'
                )
            if len(errors) == 0:
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'error': True, 'errors': errors, 'game_ids': errors_game_id})
        else:
            return JsonResponse({'error': 'No data'}, status=400)


class LoginView(View):
    def post(self, request):
        if not request.user.is_authenticated():
            json_data = json.loads(request.body.decode("utf-8"))
            username = json_data['username']
            password = json_data['password']
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                auth.login(request, user)
                our_next = request.GET.get('next')
                if our_next is not None:
                    # return HttpResponseRedirect(our_next)
                    return JsonResponse({'session_id': request.session.session_key, 'next': our_next})
                else:
                    # return HttpResponseRedirect(reverse('cm:index'))
                    return JsonResponse({'session_id': request.session.session_key, 'next': reverse("teamtrack:index")})
            else:
                return JsonResponse({'error_msg': "Your username or password is incorrect!"}, status=403)
        else:
            return HttpResponseRedirect(reverse("teamtrack:index"))

    def get(self, request):
        if not request.user.is_authenticated():
            if len(User.objects.all()) == 0:
                return HttpResponseRedirect(reverse("user:first_run"))

            c = {
                'this_week': get_closest_game_by_date(timezone.now()).week
            }
            c.update(csrf(request))

            return render(request, 'teamtrack/login.html', c)
        else:
            return HttpResponseRedirect(reverse("teamtrack:index"))


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('teamtrack:index'))


class SeePickView(View):
    def get(self, request, week):
        games = Game.objects.filter(week=week).order_by('datetime')
        users = User.objects.all().order_by('last_name')
        data = {
            'users': [],
            'games': []
        }
        for game in games:
            data['games'].append(game)
        for user in users:
            Log.i("Looking at user: %s %s" % (user.first_name, user.last_name))
            try:
                user_data = {
                    'name': '%s %s' % (user.first_name, user.last_name),
                    'user_picks': [],
                    'tie_breaker': TieBreaker.objects.get(week=week, user=user).points
                }
                for game in games:
                    user_data['user_picks'].append(Pick.objects.get(user=user, game=game))
                data['users'].append(user_data)
            except TieBreaker.DoesNotExist:
                Log.i('%s %s Does not have Tie Breaker' % (user.first_name, user.last_name))

        kwargs = {
            'this_week': get_closest_game_by_date(timezone.now()).week,
            'week': week,
            'data': data
        }
        if timezone.now() > games[0].datetime:
            kwargs['disabled'] = True

        return render(request, 'teamtrack/see.html', kwargs)


class RegisterView(View):
    def post(self, request):
        if not request.user.is_authenticated():
            json_data = json.loads(request.body.decode("utf-8"))
            try:
                new_user = User(
                    username=json_data['username'],
                    first_name=json_data['first_name'],
                    last_name=json_data['last_name']
                )
                new_user.set_password(json_data['password'])
                new_user.save()
                return JsonResponse({'success': True})
            except IntegrityError:
                return JsonResponse({'error': 'The username "%s" already exists.' % json_data['username']}, status=400)
        else:
            return JsonResponse({'error': 'Cannot register user. You are already logged in.'}, status=400)


def get_closest_game_by_date(target):
    closest_greater_qs = Game.objects.filter(datetime__gt=target).order_by('datetime')
    closest_less_qs = Game.objects.filter(datetime__lt=target).order_by('-datetime')

    try:
        try:
            closest_greater = closest_greater_qs[0]
        except IndexError:
            return closest_less_qs[0]
        try:
            closest_less = closest_less_qs[0]
        except IndexError:
            return closest_greater_qs[0]
    except IndexError:
        raise Game.DoesNotExist(
            "There is no closest object because there are no objects.")
    if closest_greater.datetime - target > target - closest_less.datetime:
        return closest_less
    else:
        return closest_greater
