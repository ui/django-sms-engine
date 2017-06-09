from django.core.management.base import BaseCommand

from sms_engine.logutils import setup_loghandlers
from sms_engine.sms import get_queued

logger = setup_loghandlers()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '-l', '--log-level', type=int,
            help='"0" to log nothing, "1" to only log errors, "2" two log all events',
        )

    def handle(self, *args, **options):
        log_level = options.get('log_level', 1)

        queued_smss = get_queued()
        logger.info('Start sending %d sms' % len(queued_smss))

        for sms in queued_smss:
            sms.dispatch(log_level=log_level)
