from sms_engine.backends import BaseSMSBackend


class Always153Backend(BaseSMSBackend):

    def send_message(self, sms):
        return 153

class DynamicBackend(BaseSMSBackend):

    def send_message(self, sms):
        # params = {
            # 'user': self.kwargs.get('user'),
            # 'pwd': self.kwargs.get('pwd'),
        # }

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
