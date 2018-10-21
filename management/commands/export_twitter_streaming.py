import logging

from tucat.core.commands import TucatExportCommand
from tucat.twitter_streaming.tasks import do_export_streaming_cmd

logger = logging.getLogger('twitter_streaming')

class Command(TucatExportCommand):
    '''
    Admin > User Command > TucatExportCommand.handle > do_cmd > do_export_cmd
    '''

    def do_cmd(self, action=None, obj=None):
        logger.debug('twitter_streaming export do_cmd %s %s %s', str(self), action, str(obj))
        do_export_streaming_cmd(action=action, obj=obj)
