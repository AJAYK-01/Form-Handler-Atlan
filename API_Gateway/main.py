from flask import Flask, request, jsonify
import requests
import os
from requests import Session

app = Flask(__name__)

# helps identify the microservice during logging
session = Session()
session.headers.update({'X-Docker-Domain': 'api_gateway'})
LOGGER_URL = os.environ.get('LOGGER_URL')
DB_HANDLER_URL = os.environ.get('DB_HANDLER_URL')


@app.route('/get-form', methods=['GET'], strict_slashes=False)
def get_form():
    ''' Fetch form to client with form id '''
    try:
        # Get the form_id parameter from the query string
        form_id = request.args.get('form_id', type=int)

        if not form_id:
            return jsonify(message='Missing form_id parameter'), 400

        # Get form data from database
        response = requests.get(
            f'{DB_HANDLER_URL}/get-form', params={'form_id': form_id}, timeout=60)
        if response.status_code != 200:
            return response.text, response.status_code
        else:
            return response.text
    except Exception as error:
        # Log Error
        log_data = {'message': str(error), 'level': 'error'}
        session.post(f'{LOGGER_URL}/log', json=log_data)

        return jsonify(message='Error occurred: check logs for details')


@app.route('/submit-form', methods=['POST'])
def submit_form():
    ''' Route to handle form submissions '''

    # Received form submission
    log_data = {'message': 'New Form Submission Received'}
    session.post(f'{LOGGER_URL}/log', json=log_data)

    try:
        data = request.json

        # # Validate form data
        # validation_response = requests.post(
        #     FORM_VALIDATION_URL, json=data, timeout=60)
        # if validation_response.status_code != 200:
        #     return validation_response.text, validation_response.status_code

        # Add form data to database
        add_to_db_response = requests.post(
            f'{DB_HANDLER_URL}/submit-response', json=data, timeout=60)
        if add_to_db_response.status_code != 200:
            return add_to_db_response.text, add_to_db_response.status_code
        else:
            return add_to_db_response.text

        # # Export form data to Google Sheets
        # export_to_sheets_response = requests.post(
        #     EXPORT_TO_SHEETS_URL, json=data, timeout=60)

        # if export_to_sheets_response.status_code != 200:
        #     return export_to_sheets_response.text, export_to_sheets_response.status_code

        # return 'Form submitted successfully', 200

    except Exception as error:
        # Log Error
        log_data = {'message': str(error), 'level': 'error'}
        session.post(f'{LOGGER_URL}/log', json=log_data)

        return jsonify(message='Error occurred: check logs for details')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=os.environ.get('DEBUG'))
