#!/bin/bash

NAME="FantasyTracker"                              # Name of the application
DJANGODIR=/webapps/fantasyfootball                       # Django project directory
SOCKFILE=/webapps/fantasyfootball/run/gunicorn.sock      # we will communicate using this unix socket
VIRTUAL_ENV=/opt/fantasyfootball                         # Virtual Environment base directory
USER=webapps                                        # the user to run as
GROUP=webapps                                       # the group to run as
NUM_WORKERS=4                                       # how many worker processes should Gunicorn spawn
DJANGO_SETTINGS_MODULE=football_picks.settings          # which settings file should Django use
DJANGO_WSGI_MODULE=football_picks.wsgi                  # WSGI module name

echo "Starting $NAME as `whoami`"

# Activate the virtual environment
cd $DJANGODIR
source ${VIRTUAL_ENV}/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Create the run directory if it doesn't exist
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec ${VIRTUAL_ENV}/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user=$USER --group=$GROUP \
  --bind=unix:$SOCKFILE \
  --log-level=info \
  --log-file=-