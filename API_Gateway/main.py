from flask import Flask, request
import requests

app = Flask(__name__)

# Replace these URLs with the actual URLs of your backend services
FORM_VALIDATION_URL = 'http://form-validation-service'
ADD_TO_DB_URL = 'http://db_handler:8080'
EXPORT_TO_SHEETS_URL = 'http://export-to-sheets-service'
LOGGING_URL = 'http://logging-service'


@app.route('/submit-form', methods=['POST'])
def submit_form():
    data = request.json

    # # Validate form data
    # validation_response = requests.post(
    #     FORM_VALIDATION_URL, json=data, timeout=60)
    # if validation_response.status_code != 200:
    #     return validation_response.text, validation_response.status_code

    # Add form data to database
    add_to_db_response = requests.post(
        f'{ADD_TO_DB_URL}/submit-response', json=data, timeout=60)
    if add_to_db_response.status_code != 200:
        return add_to_db_response.text, add_to_db_response.status_code

    # # Export form data to Google Sheets
    # export_to_sheets_response = requests.post(
    #     EXPORT_TO_SHEETS_URL, json=data, timeout=60)

    # if export_to_sheets_response.status_code != 200:
    #     return export_to_sheets_response.text, export_to_sheets_response.status_code
    # # Log successful form submission
    # log_data = {'message': 'Form submitted successfully'}
    # requests.post(LOGGING_URL, json=log_data, timeout=60)
    return 'Form submitted successfully', 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
