import requests
import os

SMS_ALERT_URL = os.environ.get('SMS_ALERT_URL')


def sms_send(phone_number):
    ''' Forward SMS data to the SMS handler '''

    data = {
        "phone_number": phone_number
    }
    response = requests.post(
        f'{SMS_ALERT_URL}/', json=data, timeout=60)

    return response.text, response.status_code
