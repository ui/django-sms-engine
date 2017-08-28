import tempfile
import sys

from django.core.management.base import BaseCommand

from sms_engine.logutils import setup_loghandlers
from sms_engine.sms import get_queued, _send_bulk

from ...lockfile import FileLock, FileLocked


logger = setup_loghandlers()
default_lockfile = tempfile.gettempdir() + "/sms_engine"


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '-l', '--log-level', type=int,
            help='"0" to log nothing, "1" to only log errors, "2" two log all events',
        )
        parser.add_argument(
            '-L', '--lockfile',
            default=default_lockfile,
            help='Absolute path of lockfile to acquire',
        )

    def handle(self, *args, **options):
        log_level = options.get('log_level', 1)

        logger.info('Acquiring lock for sending queued smss at %s.lock' %
                    options['lockfile'])

        queued_smss = get_queued()
        try:
            with FileLock(options['lockfile']):
                try:
                    while queued_smss:
                        _send_bulk(queued_smss, log_level=log_level)
                        queued_smss = get_queued()
                except Exception as e:
                    logger.error(e, exc_info=sys.exc_info(), extra={'status_code': 500})
                    raise
        except FileLocked:
            logger.info('Failed to acquire lock, terminating now.')
