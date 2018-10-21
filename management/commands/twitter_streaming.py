import logging

from tucat.application.commands import TucatCommand
from tucat.twitter_streaming.tasks import do_streaming_cmd

logger = logging.getLogger('twitter_streaming')

class Command(TucatCommand):
    '''
    Admin > User Command > TucatCommand.handle > do_cmd > do_streaming_cmd
    '''

    def do_cmd(self, action=None, obj=None):
        logger.debug('twitter_streaming do_cmd %s %s %s', str(self), action, str(obj))
        do_streaming_cmd(action, obj=obj)
