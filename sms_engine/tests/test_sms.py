from django.test import TestCase

from mock import patch

from sms_engine.models import SMS, PRIORITY, STATUS
from sms_engine.sms import create as create_sms, send as send_sms


class SMSTest(TestCase):

	def test_sms_create(self):
		create_sms(to="+62800000000001", message="Test", backend='dummy')
		sms = SMS.objects.latest('id')
		self.assertEqual(sms.to, '+62800000000001')
		self.assertEqual(sms.message, 'Test')

		# default priority is medium
		self.assertEqual(sms.priority, PRIORITY.medium)
		# if priority != now, default status is set as queued
		self.assertEqual(sms.status, STATUS.queued)

		self.assertRaises(
			ValueError, create_sms, to="+62800000000001", message="Test",
			backend="unavailable_backends"
		)

	@patch('sms_engine.models.SMS.dispatch')
	def test_sms_send(self, mock):
		send_sms(to="+62800000000001", message="Test Send", backend='dummy')
		sms = SMS.objects.latest('id')
		self.assertEqual(sms.to, '+62800000000001')
		self.assertEqual(sms.message, 'Test Send')
		self.assertEqual(sms.status, STATUS.queued)
		self.assertEqual(mock.call_count, 0)

		send_sms(to="+62800000000002", message="Test Send", backend='dummy', priority=PRIORITY.now)
		sms = SMS.objects.latest('id')
		self.assertEqual(sms.to, '+62800000000002')
		# dispatch method should be called if priority is `now`
		self.assertEqual(mock.call_count, 1)
