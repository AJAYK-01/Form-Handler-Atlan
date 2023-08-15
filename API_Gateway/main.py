from flask import Flask, request, jsonify
import requests
import os
import json
from requests import Session

from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

# helps identify the microservice during logging
session = Session()
session.headers.update({'X-Docker-Domain': 'api_gateway'})

# Fetch url enpoints from services_urls
LOGGER_URL = os.environ.get('LOGGER_URL')
DB_HANDLER_URL = os.environ.get('DB_HANDLER_URL')
FORM_VALIDATION_URL = os.environ.get('FORM_VALIDATION_URL')
GOOGLE_SHEETS_URL = os.environ.get('GOOGLE_SHEETS_URL')
SMS_ALERT_URL = os.environ.get('SMS_ALERT_URL')
SEARCH_SLANGS_URL = os.environ.get('SEARCH_SLANGS_URL')


@app.route('/create-form', methods=['POST'], strict_slashes=False)
def create_form():
    ''' Forward form creation data to the database handler '''
    response = requests.post(
        f'{DB_HANDLER_URL}/create-form', json=request.json, timeout=60)

    return response.text, response.status_code


@app.route('/get-form', methods=['GET'], strict_slashes=False)
def get_form():
    ''' Fetch form to client with form id '''
    response = requests.get(
        f'{DB_HANDLER_URL}/get-form', params=request.args, timeout=60)

    return response.text, response.status_code


@app.route('/submit-form', methods=['POST'], strict_slashes=False)
def submit_form():
    ''' Forward form submission data to the database handler '''
    response = requests.post(
        f'{DB_HANDLER_URL}/submit-response', json=request.json, timeout=60)

    return response.text, response.status_code


@app.route('/validate-response', methods=['POST'], strict_slashes=False)
def validate_response():
    ''' Forward form validation data to the database handler '''
    # Forward form validation data to the database handler
    response = requests.post(
        f'{FORM_VALIDATION_URL}/', json=request.json, timeout=60)

    return response.text, response.status_code


@app.route('/sheets-export', methods=['POST'], strict_slashes=False)
def sheets_export():
    ''' Forward form export data to the Google Sheets handler '''
    response = requests.post(
        f'{GOOGLE_SHEETS_URL}/export-form', json=request.json, timeout=60)

    return response.text, response.status_code


@app.route('/sheets-export-all', methods=['POST'], strict_slashes=False)
def sheets_export_all():
    ''' Forward all forms export data to the Google Sheets handler '''
    response = requests.post(
        f'{GOOGLE_SHEETS_URL}/export-all', json=request.json, timeout=60)

    return response.text, response.status_code


# SMS alert endpoint hidden and moved to only being used by databse handler after form submission
# @app.route('/sms-alert', methods=['POST'], strict_slashes=False)
# def sms_send():
#     ''' Forward SMS data to the SMS handler '''
#     response = requests.post(
#         f'{SMS_ALERT_URL}/', json=request.json, timeout=60)

#     return response.text, response.status_code


@app.route('/search-slangs', methods=['POST'], strict_slashes=False)
def search_slangs():
    ''' Forward slang search data to the database handler '''
    # Forward slang search data to the database handler
    response = requests.post(
        f'{SEARCH_SLANGS_URL}', json=request.json, timeout=60)

    return response.text, response.status_code


# Swagger documentation Endpoint
@app.route('/swagger.json')
def swagger_json():
    with app.open_resource('swagger.json') as f:
        swagger_data = json.load(f)
    return jsonify(swagger_data)


# Create a Swagger blueprint
SWAGGER_URL = '/swagger'
API_URL = '/swagger.json'
swagger_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "API Gateway"
    }
)
app.register_blueprint(swagger_blueprint, url_prefix=SWAGGER_URL)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=os.environ.get('DEBUG'))
