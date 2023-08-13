from sqlalchemy import create_engine, select, Table, Column, Integer, String, MetaData
from flask import Flask, request, jsonify
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from requests import Session
import os

from share import share_spreadsheet

app = Flask(__name__)

# helps identify the microservice during logging
session = Session()
session.headers.update({'X-Docker-Domain': 'google_sheets'})
LOGGER_URL = os.environ.get('LOGGER_URL')

# Google Sheets API creds
SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'google-sheets-service-key.json'


# Replace this value with your own
DATABASE_URL = os.environ.get('DATABASE_URL')

# Connect to the database using a database URL
engine = create_engine(DATABASE_URL)
conn = engine.connect()

# Set up the Google Sheets API client
credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
sheets_service = build('sheets', 'v4', credentials=credentials)


# Define the database tables
metadata = MetaData()
form_table = Table('form', metadata,
                   Column('id', Integer, primary_key=True),
                   Column('title', String),
                   )
question_table = Table('question', metadata,
                       Column('id', Integer, primary_key=True),
                       Column('form_id', Integer),
                       Column('question_text', String),
                       )
response_table = Table('response', metadata,
                       Column('id', Integer, primary_key=True),
                       Column('form_id', Integer),
                       Column('email', String),
                       )
answer_table = Table('answer', metadata,
                     Column('id', Integer, primary_key=True),
                     Column('response_id', Integer),
                     Column('question_id', Integer),
                     Column('answer_text', String),
                     )


def create_sheet(title):
    """Create a new Google Sheet and return its ID."""
    spreadsheet = {
        'properties': {
            'title': title
        }
    }
    spreadsheet = sheets_service.spreadsheets().create(
        body=spreadsheet, fields='spreadsheetId').execute()
    return spreadsheet.get('spreadsheetId')


def write_data(spreadsheet_id, sheet_name, data):
    """Write data to a Google Sheet."""

    # Check if a sheet with the same name already exists and append version number if necessary
    sheets_metadata = sheets_service.spreadsheets().get(
        spreadsheetId=spreadsheet_id).execute()
    sheets = sheets_metadata.get('sheets', '')
    sheet_names = [sheet.get("properties", {}).get("title", "")
                   for sheet in sheets]

    version_number = 1
    new_sheet_name = sheet_name

    while new_sheet_name in sheet_names:
        new_sheet_name = f'{sheet_name} v{version_number}'
        version_number += 1

    body = {
        'requests': [{
            'addSheet': {
                'properties': {
                    'title': new_sheet_name
                }
            }
        }]
    }
    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id, body=body).execute()
    body = {
        'values': data
    }
    range_ = f'{new_sheet_name}!A1'
    sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=range_, valueInputOption='RAW', body=body).execute()


@app.route('/export-all', methods=['POST'], strict_slashes=False)
def export_all():
    """Export all forms and their associated data to Google Sheets."""

    try:
        req_body = request.json
        email = req_body['email']

        # Create a new Google Sheet
        spreadsheet_id = create_sheet(f'All Forms for {email}')

        # Query the database for all forms
        query = select(form_table.c.id, form_table.c.title)
        result = conn.execute(query)
        forms = result.fetchall()

        # Export each form and its associated data
        for form_id, form_title in forms:
            # Export question data
            result = conn.execute(
                select(question_table.c.id, question_table.c.question_text)
                .where(question_table.c.form_id == form_id))
            questions = result.fetchall()

            # Export response data
            result = conn.execute(
                select(response_table.c.id, response_table.c.email)
                .where(response_table.c.form_id == form_id))
            responses = result.fetchall()

            # Create header row with question text as column names
            header_row = ['Response ID', 'Email'] + [row[1]
                                                     for row in questions]

            response_data = [header_row]

            for response in responses:
                response_row = list(response)

                # Get answers for this response and add them to the row
                result = conn.execute(
                    select(answer_table.c.question_id,
                           answer_table.c.answer_text)
                    .where(answer_table.c.response_id == response[0]))
                answers = result.fetchall()
                answer_dict = {row[0]: row[1] for row in answers}
                response_row += [answer_dict.get(question[0], '')
                                 for question in questions]

                response_data.append(response_row)

            write_data(spreadsheet_id, form_title, response_data)

        # Delete default "Sheet1"
        body = {
            'requests': [{
                'deleteSheet': {
                    'sheetId': 0
                }
            }]
        }
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id, body=body).execute()

        res = share_spreadsheet(spreadsheet_id, email=email, creds=credentials)

        # Log that all forms were exported
        log_data = {'message': f'Exported all forms for {email}'}
        session.post(f'{LOGGER_URL}/log', json=log_data)

        return jsonify(message=res)

    except Exception as error:
        # Log Error
        log_data = {'message': str(error), 'level': 'error'}
        session.post(f'{LOGGER_URL}/log', json=log_data)

        return jsonify(message='Error occurred: check logs for details'), 500


@app.route('/export-form', methods=['POST'], strict_slashes=False)
def export_form():
    """Export a single form and its associated data to Google Sheets."""

    try:
        req_body = request.json
        email = req_body['email']
        form_id = req_body['form_id']

        # Query the database for the form data
        result = conn.execute(
            select(form_table.c.title).where(form_table.c.id == form_id))
        row = result.fetchone()

        if row is None:
            # Log Error
            log_data = {
                'message': f'Form with ID {form_id} does not exist', 'level': 'error'}
            session.post(f'{LOGGER_URL}/log', json=log_data)

            return jsonify(message=f'Form with ID {form_id} does not exist'), 400

        form_title = row[0]

        # Create a new Google Sheet
        spreadsheet_id = create_sheet(f'{form_title}')

        # Export question data
        result = conn.execute(
            select(question_table.c.id, question_table.c.question_text)
            .where(question_table.c.form_id == form_id))

        questions = result.fetchall()

        # Export response data
        result = conn.execute(
            select(response_table.c.id, response_table.c.email)
            .where(response_table.c.form_id == form_id))

        responses = result.fetchall()

        # Create header row with question text as column names
        header_row = ['Response ID', 'Email'] + [row[1] for row in questions]

        response_data = [header_row]

        for response in responses:
            response_row = list(response)

            # Get answers for this response and add them to the row
            result = conn.execute(
                select(answer_table.c.question_id, answer_table.c.answer_text)
                .where(answer_table.c.response_id == response[0]))

            answers = result.fetchall()
            answer_dict = {row[0]: row[1] for row in answers}
            response_row += [answer_dict.get(question[0], '')
                             for question in questions]

            response_data.append(response_row)

        write_data(spreadsheet_id, form_title, response_data)

        # Delete default "Sheet1"
        body = {
            'requests': [{
                'deleteSheet': {
                    'sheetId': 0
                }
            }]
        }
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id, body=body).execute()

        res = share_spreadsheet(spreadsheet_id, email=email, creds=credentials)

        # Log that a single form was exported
        log_data = {'message': f'Exported form with ID: {form_id}'}
        session.post(f'{LOGGER_URL}/log', json=log_data)

        return jsonify(message=res)

    except Exception as error:
        # Log Error
        log_data = {'message': str(error), 'level': 'error'}
        session.post(f'{LOGGER_URL}/log', json=log_data)

        return jsonify(message='Error occurred: check logs for details'), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=os.environ.get('DEBUG'))
