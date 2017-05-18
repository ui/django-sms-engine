from django.conf import settings

from twilio.rest import Client


class BaseSMSBackend:
    """
    Base class for sms backend implementations
    Subclasses must at least overwrite send_messages().

    """

    def __init__(self, sms):
        self.to = sms.to
        self.message = sms.message

    def send_message(self):
        raise NotImplementedError('subclasses of BaseSMSBackend must override send_message() method')


class TwilioBackend(BaseSMSBackend):

    def send_message(self):
        client = Client(settings.twilio_sid,
                        settings.twilio_auth_token)

        client.api.account.messages.create(from_=settings.TWILIO_FROM_NUMBER,
                                           to=self.to,
                                           body=self.message)
