from django.test import TestCase

from sms_engine.backends import BaseSMSBackend
from sms_engine.exceptions import SendSMSError
from sms_engine.models import SMS, STATUS


class RaiseExceptionBackend(BaseSMSBackend):
    '''
        The utility of this backend only to raise exception error
    '''
    def send_message(self, sms):
        raise SendSMSError('SMS sending error')


class ModelsTest(TestCase):

    def test_dispatch(self):
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

        backend_settings = {
            'BACKENDS': {
                'exception': 'sms_engine.tests.test_models.RaiseExceptionBackend'
            }
        }

        SMS.objects.all().delete()
        with self.settings(SMS_ENGINE=backend_settings):
            sms = SMS.objects.create(
                to='+6280000000000', message='test', backend_alias='exception'
            )
            sms.dispatch()

            self.assertEqual(sms.status, STATUS.failed)

            log = sms.logs.first()
            self.assertEqual(log.message, 'SMS sending error')
            self.assertEqual(log.exception_type, 'SendSMSError')
