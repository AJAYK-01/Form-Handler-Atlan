from sqlalchemy import create_engine, select, Table, Column, Integer, String, TIMESTAMP, cast, MetaData
from flask import Flask, request, jsonify
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from requests import Session
import os

from Sheets_Service.interface import GoogleSheets

app = Flask(__name__)

# helps identify the microservice during logging
session = Session()
session.headers.update({'X-Docker-Domain': 'google_sheets'})
LOGGER_URL = os.environ.get('LOGGER_URL')


# Replace this value with your own
DATABASE_URL = os.environ.get('DATABASE_URL')

# create Google Sheets instance
sheets = GoogleSheets()

# Connect to the database using a database URL
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
conn = engine.connect()


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
                       Column('phone', String),
                       Column('submitted_at', TIMESTAMP)
                       )
answer_table = Table('answer', metadata,
                     Column('id', Integer, primary_key=True),
                     Column('response_id', Integer),
                     Column('question_id', Integer),
                     Column('answer_text', String),
                     )


def export_form_data(form_id, spreadsheet_id, form_title):
    """Export form data for a single form to a Google Sheet."""

    # Export question data
    result = conn.execute(
        select(question_table.c.id, question_table.c.question_text)
        .where(question_table.c.form_id == form_id))
    questions = result.fetchall()

    # Export response data
    result = conn.execute(
        select(response_table.c.id, response_table.c.email,
               response_table.c.phone, cast(response_table.c.submitted_at, String))
        .where(response_table.c.form_id == form_id))
    responses = result.fetchall()

    # Create header row with question text as column names
    header_row = ['Response No', 'Email', 'Phone', 'Submitted At'] + [row[1]
                                                                      for row in questions]

    response_data = [header_row]

    serial_no = 1
    for response in responses:
        response_row = [serial_no] + list(response)[1:]

        # Get answers for this response and add them to the row
        result = conn.execute(
            select(answer_table.c.question_id,
                   answer_table.c.answer_text)
            .where(answer_table.c.response_id == response[0]))
        answers = result.fetchall()
        answer_dict = {row[0]: row[1] for row in answers}

        for _, values in answer_dict.items():
            response_row.append(values)

        response_data.append(response_row)
        serial_no += 1

    sheets.write_data(spreadsheet_id=spreadsheet_id,
                      sheet_name=form_title, data=response_data)


@app.route('/export-all', methods=['POST'], strict_slashes=False)
def export_all():
    """Export all forms and their associated data to Google Sheets."""

    try:
        req_body = request.json
        email = req_body['email']

        # Create a new Google Sheet
        spreadsheet_id = sheets.create_sheet(
            title=f'All Forms for {email}')

        # Query the database for all forms
        query = select(form_table.c.id, form_table.c.title)
        result = conn.execute(query)
        forms = result.fetchall()

        # Export each form and its associated data
        for form_id, form_title in forms:
            export_form_data(form_id, spreadsheet_id, form_title)

        # Delete default "Sheet1"
        sheets.delete_default_sheet(spreadsheet_id=spreadsheet_id)

        res = sheets.share_spreadsheet(
            spreadsheet_id=spreadsheet_id, email=email)

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
        spreadsheet_id = sheets.create_sheet(title=f'{form_title}')

        export_form_data(form_id, spreadsheet_id, form_title)

        # Delete default "Sheet1"
        sheets.delete_default_sheet(spreadsheet_id=spreadsheet_id)

        res = sheets.share_spreadsheet(
            spreadsheet_id=spreadsheet_id, email=email)

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
