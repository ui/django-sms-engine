from django.db import connection
from django.conf import settings
from django.test import TransactionTestCase

from mock import patch
from requests.exceptions import ConnectTimeout
from sms_engine.models import SMS, STATUS, Backend


class ModelsTest(TransactionTestCase):

    def test_dispatch(self):
        backend = Backend.objects.create(alias="dummy")
        sms = SMS.objects.create(
            to='+6280000000000', message='test', backend_alias='dummy'
        )
        sms.dispatch(log_level=2)
        sms = SMS.objects.latest('id')
        self.assertEqual(sms.to, '+6280000000000')
        self.assertEqual(sms.status, STATUS.sent)
        self.assertEqual(sms.logs.first().status, STATUS.sent)

        SMS.objects.all().delete()

        sms = SMS.objects.create(
            to='+6280000000000', message='test', backend_alias='dummy'
        )
        sms.dispatch(log_level=0)
        self.assertEqual(sms.status, STATUS.sent)
        self.assertFalse(sms.logs.exists())

        SMS.objects.all().delete()
        backend.alias = "error"
        backend.save()

        sms = SMS.objects.create(
            to='+6280000000000', message='test', backend_alias='error'
        )
        sms.dispatch()

        self.assertEqual(sms.status, STATUS.failed)

        log = sms.logs.first()
        self.assertEqual(log.message, 'SMS sending error')
        self.assertEqual(log.exception_type, 'SendSMSError')

        backend.alias = "dummy"
        backend.save()
        
        # retry on correct exceptions
        settings.SMS_ENGINE['MAX_RETRIES'] = 2
        settings.SMS_ENGINE['EXCEPTIONS_TO_RETRY'] = set([ConnectTimeout])
        with patch('sms_engine.backends.DummyBackend.send_message',
                   side_effect=ConnectTimeout()):
            sms = SMS.objects.create(
                to="+6281314855365",
                message="test",
            )

            # Commit=False (bulk sending), expect any errors to be bubbled up
            with self.assertRaises(ConnectTimeout):
                sms.dispatch(commit=False)
            log = sms.logs.first()
            self.assertEqual(log.exception_type, 'ConnectTimeout')