import datetime

from django.core.management.base import BaseCommand
from django.db import connection
from django.utils.timezone import now

from ...models import Log, SMS


class Command(BaseCommand):
    help = 'Place deferred messages back in the queue.'

    def add_arguments(self, parser):
        parser.add_argument('-d', '--days',
            type=int,
            default=90,
            help="Cleanup smses older than this many days, defaults to 90."
        )

    def handle(self, verbosity, days, **options):
        # Delete smses and their related logs created before X days

        cutoff_date = now() - datetime.timedelta(days)
        count = SMS.objects.filter(created__lt=cutoff_date).count()

        Log.objects.filter(sms__created__lt=cutoff_date).delete()
        cursor = connection.cursor()
        query = 'DELETE FROM "sms_engine_sms" WHERE "sms_engine_sms"."created" < "%s"' % \
                cutoff_date.strftime('%Y-%m-%dT%H%M%S.%f')
        cursor.execute(query)

        print("Deleted {0} mails created before {1} ".format(count, cutoff_date))
