#!/bin/bash

python manage.py dumpdata twitter_streaming.exportationformat --indent 4 -o ~/twitter_streaming.exportationformat.json
python manage.py dumpdata twitter_streaming.twitterliststreaming --indent 4 -o ~/twitter_streaming.twitterliststreaming.json
python manage.py dumpdata django_celery_beat.intervalschedule --indent 4 -o ~/django_celery_beat.intervalschedule.json
python manage.py dumpdata django_celery_beat.periodictask --pks 2 --indent 4 -o ~/django_celery_beat.periodictask.json
