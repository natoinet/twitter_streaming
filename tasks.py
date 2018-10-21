from __future__ import absolute_import

import logging
import subprocess
from datetime import datetime
from pathlib import Path
import re

from django.conf import settings
from django.core.files import File
from django_celery_beat.models import PeriodicTask

from celery import task
from celery.app.task import Task

from pymongo import MongoClient

import requests
from requests_oauthlib import OAuth1

from tucat.core.base import add_dt_to_json
from tucat.core.token import get_app_token, get_users_token
from tucat.application.models import TucatApplication
from tucat.twitter_streaming.models import TwitterListStreaming, TwitterListStreamingExport

logger = logging.getLogger('twitter_streaming')


def do_streaming_cmd(action=None, obj=None):
    logger.info('do_cmd %s', action)

    #one_app = TucatApplication.objects.get(package_name=__package__)
    one_app = TucatApplication.objects.get(pk=obj.pk)
    periodic_streaming = PeriodicTask.objects.get(name=__package__)
    periodic_streaming.args = [obj.pk]
    periodic_streaming.save()

    if (action is 'run'):
        logger.info('Running')
        periodic_streaming.enabled = True
        periodic_streaming.save()
        one_app.update(status='r')
    elif (action is 'stop'):
        logger.info('Stopping')
        periodic_streaming.enabled = False
        periodic_streaming.save()
        one_app.update(status='s')
    else:
        logger.info('Unknown command')

@task
def do_run(obj_pk):
    try:
        logger.info('do_run streaming')

        db_name = __package__.replace('.', '_')
        one_app = TucatApplication.objects.get(pk=obj_pk)
        tucat_elements = TwitterListStreaming.objects.filter(application_id=one_app.id, is_enabled=True)

        for element in tucat_elements:
            logger.info('do_run streaming %s %s', element.owner_name, element.list_name)
            tw_streaming(owner_name=element.owner_name, list_name=element.list_name)
            #colname = get_collection_name(element.owner_name, element.list_name)
            #add_dt_to_mongo( db_name, colname, ['created_at'] )

        one_app.update(status='r')

        logger.info('do_run streaming success')
    except Exception as e:
        logger.exception(e)
        one_app.update(status='f')
        periodictask = PeriodicTask.objects.get(name=__package__)
        periodictask.enabled = False
        periodictask.save()

    finally:
        logger.info('file:%s | finally', __file__)

def tw_streaming(owner_name='', list_name=''):
    logger.info('tw_streaming start %s %s', owner_name, list_name)

    app_token = get_app_token('twitter')
    users_token = get_users_token ('twitter')

    colname = get_collection_name(owner_name, list_name)
    #oauth = OAuth1(CONSUMER['key'], CONSUMER['secret'], TOKEN['key'], TOKEN['secret'], signature_type='auth_header')
    oauth = OAuth1(app_token['key'], app_token['secret'], users_token[0]['key'], users_token[0]['secret'], signature_type='auth_header')

    url = 'https://api.twitter.com/1.1/lists/statuses.json'
    parameters = {'owner_screen_name' : owner_name, 'slug' : list_name, 'include_rts' : '1'}

    since_id = get_since_id(colname)
    if (since_id > 0):
        logger.debug('since_id: %s', since_id)
        parameters['since_id'] = since_id
    else:
        parameters['count'] = '200'

    logger.info('url:%s | parameters:%s | auth:%s', url, parameters, str(oauth))

    request = requests.get(url=url, params=parameters, auth=oauth)

    _todb(colname, request)

def get_collection_name(owner_name, list_name):
    return owner_name + '-' + list_name

def get_since_id(colname):
    db_name = __package__.replace('.', '_')
    logger.debug('filename:%s | db: %s', __file__, db_name)

    db = MongoClient(settings.MONGO_CLIENT)[db_name]

    if (db[colname].find().count() > 0):
        since_id = db[colname].find().limit(1).sort([('$natural',1)])[0]['id']
    else:
        since_id = -1

    return since_id

def _todb(colname, request):

    if (request.status_code != 200):
        logger.critical('StreamingApi.getJson status code %s \nrequest %s',
            request.status_code, request)
        raise Exception("Status code is not 200: ", request.status_code)
    else:
        db_name = __package__.replace('.', '_')
        logger.debug('filename:%s | db: %s | collection:%s | original json: %s', __file__, db_name, colname, request.json())
        db = MongoClient(settings.MONGO_CLIENT)[db_name]
        json_list = request.json()

        logger.debug('before for')

        for one_json in json_list:
            # Duplicate removal
            if (db[colname].find({'id' : one_json['id']}).count() == 0):
                # For export date filter
                one_json = add_dt_to_json(one_json, ['created_at'])
                db[colname].insert(one_json)
                logger.debug('filename:%s | db: %s | collection:%s | modified json: %s', __file__, db_name, colname, one_json)

@task(bind=True)
def do_run_export(self, obj_pk):
    logger.info('do_run_export')

    try:
        export = TwitterListStreamingExport.objects.get(pk=obj_pk)

        output = None
        db_name = __package__.replace('.', '_')
        #out_folder = str(Path(__file__).parents[1] / 'media/output')
        out_folder = str(settings.APPS_DIR.path('media')) + '/output'
        out_file = output
        export.update(self.request.id, 'r')

        path = str(Path(__file__).parent / 'export') + '/'

        colname = get_collection_name(export.list.owner_name, export.list.list_name)

        #export_type = ExportationType.objects.get(pk=export_type_id)
        logger.info('do_run_export %s %s %s to %s', export.export_format, export.before, export.after, path)

        if export.before is None and export.after is None :
            if export.export_format.format == 'json':
                output = subprocess.check_output([path + export.export_format.format + '-twitter_streaming.sh', db_name, colname , out_folder])
            else:
                output = subprocess.check_output([path + export.export_format.format + '-twitter_streaming.sh', db_name, colname, out_folder, export.export_format.fields])
        else:
            epoch_before = '0'
            epoch_after = datetime.utcnow().strftime('%s') + '000'

            if export.before is not None :
                epoch_before = export.before.strftime('%s') + '000'
            if export.after is not None :
                epoch_after = export.after.strftime('%s') + '000'

            if (export.export_format.format == 'json'):
                output = subprocess.check_output([path + export.export_format.format + '-twitter_streaming-after.sh', db_name, colname, out_folder, epoch_before, epoch_after])
            else:
                #subprocess.call([path + 'friendsgraph-lasttweet.sh', str(export.collection), epoch_lt, path])
                output = subprocess.check_output([path + export.export_format.format + '-twitter_streaming-after.sh', db_name, colname, out_folder, export.export_format.fields, epoch_before, epoch_after])

        logger.info('do_run_export output %s', output)
        #export.link_file = output.decode("utf-8")

        result = output.decode("utf-8")
        logger.debug('do_run_export out_file %s', result)
        out_file = re.findall(r"\S+", result)[0]
        logger.debug('do_run_export out_file %s', result)

        with open(out_folder  + '/' + out_file, 'r') as f:
            export.file = File(f)
            export.save()

        export.update(self.request.id, 'c')

    except Exception as e:
        logger.exception(e)
        export.update(self.request.id, 'f')

def do_stop_export(obj_pk):
    logger.info('do_stop_export')
    export = TwitterListStreamingExport.objects.get(pk=obj_pk)

    try:
        logger.info('do_stop_export locked task_id %s', export.task_id)
        app.control.revoke(export.task_id, terminate=True)
        logger.info('do_stop_export: Task revoked')

        export.update('', 's')

    except Exception as e:
        logger.exception(e)

def do_export_streaming_cmd(action=None, obj=None):
    logger.info('do_export_cmd %s %s %s %s %s %s %s', action, obj, obj.export_format, obj.export_format.fields, obj.list, obj.before, obj.after)

    if (action is 'run'):
        logger.info('do_export_cmd running')
        do_run_export.apply_async((obj.pk,))

#        do_run_export.apply_async(kwargs={'export_type_id': obj.export_type.pk, 'collection': obj.collections.pk, 'last_tweet' : obj.last_tweet})
    elif (action is 'stop'):
        logger.info('do_export_cmd stopping')
        do_stop_export(obj.pk)
    else:
        logger.info('Unknown command')
