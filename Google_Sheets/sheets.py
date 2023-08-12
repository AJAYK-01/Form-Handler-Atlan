from sqlalchemy import create_engine, select, Table, Column, Integer, String, MetaData
from flask import Flask, request, jsonify
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from requests import Session
import psycopg2
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
    body = {
        'requests': [{
            'addSheet': {
                'properties': {
                    'title': sheet_name
                }
            }
        }]
    }
    sheets_service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id, body=body).execute()
    body = {
        'values': data
    }
    range_ = f'{sheet_name}!A1'
    sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=range_, valueInputOption='RAW', body=body).execute()


@app.route('/export-all', methods=['POST'], strict_slashes=False)
def export_all():
    """Export all forms and their associated data to Google Sheets."""

    req_body = request.json
    email = req_body['email']

    # Create a new Google Sheet
    spreadsheet_id = create_sheet('All Forms')

    # Query the database for all forms
    query = select(form_table.c.id, form_table.c.title)
    result = conn.execute(query)
    forms = result.fetchall()

    # Export each form and its associated data
    for form_id, form_title in forms:
        # Export form data
        form_data = [[form_title]]
        write_data(spreadsheet_id, f'Form {form_id}', form_data)

        # Export question data
        result = conn.execute(
            select(question_table.c.id, question_table.c.question_text).where(question_table.c.form_id == form_id))
        questions = result.fetchall()
        question_data = [['ID', 'Question Text']] + \
            [list(row) for row in questions]
        write_data(spreadsheet_id, f'Form {form_id} Questions', question_data)

        # Export response data
        result = conn.execute(
            select(response_table.c.id, response_table.c.email).where(response_table.c.form_id == form_id))
        responses = result.fetchall()
        response_data = [['ID', 'Email']] + [list(row) for row in responses]
        write_data(spreadsheet_id, f'Form {form_id} Responses', response_data)

        # Export answer data
        result = conn.execute(
            select(answer_table.c.id, answer_table.c.response_id, answer_table.c.question_id, answer_table.c.answer_text))
        answers = result.fetchall()
        answer_data = [['ID', 'Response ID',
                        'Question ID', 'Answer Text']] + [list(row) for row in answers]
        write_data(spreadsheet_id, f'Form {form_id} Answers', answer_data)

    res = share_spreadsheet(spreadsheet_id, email=email, creds=credentials)

    return jsonify(message=res)


@app.route('/export-form', methods=['POST'], strict_slashes=False)
def export_form():
    """Export a single form and its associated data to Google Sheets."""

    req_body = request.json
    email = req_body['email']
    form_id = req_body['form_id']

    # Create a new Google Sheet
    spreadsheet_id = create_sheet(f'Form {form_id}')

    # Query the database for the form data
    result = conn.execute(
        select(form_table.c.title).where(form_table.c.id == form_id))
    form_title = result.fetchone()[0]

    # Export form data
    form_data = [[form_title]]
    write_data(spreadsheet_id, f'Form {form_id}', form_data)

    # Export question data
    result = conn.execute(
        select(question_table.c.id, question_table.c.question_text).where(question_table.c.form_id == form_id))
    questions = result.fetchall()
    question_data = [['ID', 'Question Text']] + \
        [list(row) for row in questions]
    write_data(spreadsheet_id, f'Form {form_id} Questions', question_data)

    # Export response data
    result = conn.execute(
        select(response_table.c.id, response_table.c.email).where(response_table.c.form_id == form_id))
    responses = result.fetchall()
    response_data = [['ID', 'Email']] + [list(row) for row in responses]
    write_data(spreadsheet_id, f'Form {form_id} Responses', response_data)

    # Export answer data
    result = conn.execute(
        select(answer_table.c.id, answer_table.c.response_id, answer_table.c.question_id, answer_table.c.answer_text))
    answers = result.fetchall()
    answer_data = [['ID', 'Response ID',
                    'Question ID', 'Answer Text']] + [list(row) for row in answers]
    write_data(spreadsheet_id, f'Form {form_id} Answers', answer_data)

    res = share_spreadsheet(spreadsheet_id, email=email, creds=credentials)

    return jsonify(message=res)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=os.environ.get('DEBUG'))
