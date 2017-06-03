from django.test import TestCase
from django.test.utils import override_settings

from sms_engine import sms
from sms_engine.models import SMS, STATUS, PRIORITY
from sms_engine.settings import get_backend, get_available_backends


class BackendTest(TestCase):

	dummy_backend = {'BACKENDS': {'twilio': 'sms_engine.backends.TwilioBackend'}}

	@override_settings(SMS_ENGINE=dummy_backend)
	def test_email_backend(self):
		"""
        Ensure that email backend properly queue email messages.
        """
		sms.send(to="+6285819651345", message="Test")
		sms_ = SMS.objects.latest('id')
		self.assertEqual(sms_.to, '+6285819651345')
		self.assertEqual(sms_.status, STATUS.queued)
		self.assertEqual(sms_.priority, PRIORITY.medium)

	def test_email_backend_settings(self):
		self.assertEqual(get_backend('nadyne'), 'sms_engine.backends.NadyneBackend')
		self.assertEqual(get_available_backends(), {
			'dummy': 'sms_engine.backends.DummyBackend',
			'twilio': 'sms_engine.backends.TwilioBackend',
			'nadyne': 'sms_engine.backends.NadyneBackend'
		})

		with self.settings(SMS_ENGINE={}):
			# If no sms backend is set, backend should default to Twilio Backend
			self.assertEqual(get_backend(), 'sms_engine.backends.TwilioBackend')

			# if no backend is set, get_available_backends() always return twilio backend by default
			self.assertEqual(get_available_backends(), {'default': 'sms_engine.backends.TwilioBackend'})
