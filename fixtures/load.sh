#!/bin/bash

python manage.py makemigrations twitter_streaming
python manage.py migrate --fake-initial

python manage.py loaddata tucat/twitter_streaming/fixtures/application.json
