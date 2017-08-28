from .exceptions import SendSMSError


class BaseSMSBackend:
    """
    Base class for sms backend implementations
    Subclasses must at least overwrite send_messages().

    """

    def send_message(self, sms):
        raise NotImplementedError('subclasses of BaseSMSBackend must override send_message() method')


class DummyBackend(BaseSMSBackend):

    def send_message(self, sms):
        response = {
            'transaction_id': '123456789',
            'status': 'sent'
        }
        return response


class ErrorBackend1(BaseSMSBackend):
    '''
        The utility of this backend only to raise exception error
    '''
    def send_message(self, sms):
        raise SendSMSError('SMS sending error')
