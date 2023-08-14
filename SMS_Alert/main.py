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


@app.route('/', methods=['POST'], strict_slashes=False)
def send_sms():
    ''' To send sms receipt for response submission '''
    try:
        data = request.json
        customer_phone_number = data.get('phone_number')
        # Message content
        message_content = 'Your Response has been submitted. Thank you.'
        # Send the SMS

        message = client.messages.create(
            to=customer_phone_number,
            from_=twilio_number,
            body=message_content)

        # Log that an SMS was sent
        log_data = {'message': f'Sent SMS to {customer_phone_number}'}
        session.post(f'{LOGGER_URL}/log', json=log_data)

        return {'status': message.status}

    except Exception as error:
        # Log Error
        log_data = {'message': str(error), 'level': 'error'}
        session.post(f'{LOGGER_URL}/log', json=log_data)

        return jsonify(message='Error occurred: check logs for details'), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=os.environ.get('DEBUG'))
