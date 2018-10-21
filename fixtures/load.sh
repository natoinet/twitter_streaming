#!/bin/bash
APP_PATH=tucat/twitter_streaming/fixtures/

python manage.py makemigrations twitter_streaming
python manage.py migrate --fake-initial

function importfixtures {
  for fixture in "$@"
  do
    if [ -e $APP_PATH$fixture.json ]
    then
      echo "Importing $fixture"
      python manage.py loaddata $APP_PATH$fixture.json
    else
      echo "No $fixture to import"
    fi
  done
}

importfixtures application twitter_streaming.exportationformat twitter_streaming.twitterliststreaming django_celery_beat.intervalschedule django_celery_beat.periodictask
