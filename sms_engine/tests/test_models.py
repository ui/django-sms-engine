from django.test import TestCase

from sms_engine.models import SMS, STATUS, Backend


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

        SMS.objects.all().delete()

        sms = SMS.objects.create(
            to='+6280000000000', message='test', backend_alias='error'
        )
        sms.dispatch()

        self.assertEqual(sms.status, STATUS.failed)

        log = sms.logs.first()
        self.assertEqual(log.message, 'SMS sending error')
        self.assertEqual(log.exception_type, 'SendSMSError')

    def test_flatten_backends(self):
        backends = {
            Backend.PRIORITY.high: ['anomali_nadyne', 'anomali_jatis'],
            Backend.PRIORITY.normal: ['anomali_twilio'],
            Backend.PRIORITY.low: ['anomali_ims'],
        }

        flattened = Backend.flatten(backends)
        self.assertIn('anomali_nadyne', flattened)
        self.assertIn('anomali_jatis', flattened)
        self.assertIn('anomali_twilio', flattened)
        self.assertIn('anomali_ims', flattened)

        # Repeat backends until min_backends
        backends = {
            Backend.PRIORITY.high: ['anomali_nadyne', 'anomali_jatis'],
            Backend.PRIORITY.normal: [],
            Backend.PRIORITY.low: [],
        }
        flattened = Backend.flatten(backends, min_backends=5)
        self.assertEqual(len(flattened), 5)
        self.assertIn('anomali_nadyne', flattened)
        self.assertIn('anomali_jatis', flattened)
        self.assertNotIn('anomali_twilio', flattened)
        self.assertNotIn('anomali_ims', flattened)

        backends = {
            Backend.PRIORITY.high: ['anomali_nadyne'],
            Backend.PRIORITY.normal: [],
            Backend.PRIORITY.low: [],
        }
        flattened = Backend.flatten(backends, min_backends=5)
        expected_flattened = ['anomali_nadyne', 'anomali_nadyne', 'anomali_nadyne',
                              'anomali_nadyne', 'anomali_nadyne']
        self.assertEqual(flattened, expected_flattened)

        # Empty backends, empty list should be returned
        backends = {
            Backend.PRIORITY.high: [],
            Backend.PRIORITY.normal: [],
            Backend.PRIORITY.low: [],
        }
        flattened = Backend.flatten(backends, min_backends=5)
        self.assertEqual(flattened, [])
