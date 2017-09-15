from django.test import TestCase

from sms_engine import sms
from sms_engine.models import SMS, STATUS, PRIORITY
from sms_engine.settings import get_backend, get_available_backends


class BackendTest(TestCase):

    def test_email_backend(self):
        """
        Ensure that email backend properly queue email messages.
        """
        sms.send(to="+62800000000001", message="Test", backend='dummy')
        sms_ = SMS.objects.latest('id')
        self.assertEqual(sms_.to, '+62800000000001')
        self.assertEqual(sms_.status, STATUS.queued)
        self.assertEqual(sms_.priority, PRIORITY.medium)

    def test_email_backend_settings(self):
        self.assertEqual(get_backend('dummy'), 'sms_engine.backends.DummyBackend')
        self.assertEqual(get_available_backends(), {
            'dummy': 'sms_engine.backends.DummyBackend',
            'error': 'sms_engine.backends.ErrorBackend1',
        })

        with self.settings(SMS_ENGINE={}):
            # if no backend is set, get_available_backends() always return dummy backend by default
            self.assertEqual(get_available_backends(), {'default': 'sms_engine.backends.DummyBackend'})
