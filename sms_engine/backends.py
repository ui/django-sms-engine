from django.conf import settings

from .exceptions import SendSMSError


class BaseSMSBackend:
    """
    Base class for sms backend implementations
    Subclasses must at least overwrite send_messages().

    """

    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs

    def send_message(self, sms):
        raise NotImplementedError('subclasses of BaseSMSBackend must override send_message() method')


class DummyBackend(BaseSMSBackend):

    def send_message(self, sms):
        return '123456789'


class RaiseExceptionBackend(BaseSMSBackend):
    '''
        The utility of this backend only to raise exception error
    '''
    def send_message(self, sms):
        raise SendSMSError('SMS sending error')


class Always153Backend(BaseSMSBackend):

    def send_message(self, sms):
        params = {
            'user': 153,
            'pwd': 153,
            'sender': 153,
            'msisdn': sms.to,
            'message': sms.message,
            'description': sms.description
        }

        # Example of sending
        # response = requests.get("http://always153.provider.com/sms.php", params=params)
        # if response.status_code == 200:
        #    status = ET.fromstring(response.content).find('Status').text
        #    if status != "SENT":
        #        raise SendSMSError(status)
        #    else:
        #        return ET.fromstring(response.content).find('TrxID').text
        # raise SendSMSError("Network Error")

        sms_id_from_provider = 153
        return sms_id_from_provider


class DynamicBackend(BaseSMSBackend):

    def send_message(self, sms):
        """ We can have this backend send from multiple accounts on this provider
        """
        params = {
            'user': self.kwargs.get('user'),
            'pwd': self.kwargs.get('pwd'),
        }

        # Example of responding
        # response = requests.get("http://dynamic.provider.com/sms.php", params=params)
        # if response.status_code == 200:
        #    status = ET.fromstring(response.content).find('Status').text
        #    if status != "SENT":
        #        raise SendSMSError(status)
        #    else:
        #        return ET.fromstring(response.content).find('TrxID').text
        # raise SendSMSError("Network Error")
        sms_id_from_provider = 155
        return sms_id_from_provider
