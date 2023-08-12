from flask import Flask, request, jsonify
from twilio.rest import Client
from requests import Session

import os

app = Flask(__name__)

# helps identify the microservice during logging
session = Session()
session.headers.update({'X-Docker-Domain': 'sms_alert'})
LOGGER_URL = os.environ.get('LOGGER_URL')

# Your Twilio Account Sid and Auth Token
account_sid = os.environ.get('TWILIO_ACC_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
twilio_number = os.environ.get('TWILIO_NUMBER')
client = Client(account_sid, auth_token)


@app.route('/send-sms', methods=['POST'], strict_slashes=False)
def send_sms():
    ''' To send sms receipt for response submission '''

    data = request.json
    customer_phone_number = data.get('phone_number')
    # Message content
    message_content = 'Your Response has been submitted. Thank you.'
    # Send the SMS

    message = client.messages.create(
        to=customer_phone_number,
        from_=twilio_number,
        body=message_content)

    return {'status': str(message)}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=os.environ.get('DEBUG'))
