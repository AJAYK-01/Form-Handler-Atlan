import os
import re
from flask import Flask, request, jsonify
from sqlalchemy import text, create_engine

from requests import Session

app = Flask(__name__)

# helps identify the microservice during logging
session = Session()
session.headers.update({'X-Docker-Domain': 'form_validation'})
LOGGER_URL = os.environ.get('LOGGER_URL')

# Database connection
DATABASE_URL = os.environ.get('DATABASE_URL')
engine = create_engine(DATABASE_URL)


@app.route('/', methods=['POST'])
def validate_response():
    '''
      Validates the forms as per rules required by client 
      It is expected that the frontend would send sql queries based on the client's validation rules
      The SQL query should be such that no rows should be returned if all rows valid
      The rule-violating-rows should be returned  
    '''
    try:
        data = request.json
        form_id = data.get('form_id')
        validation_query = data.get('validation_query')

        # Check if the query contains any database modification keywords at the beginning of an SQL command using a regular expression
        if re.search(r'\b(insert|update|delete)\b', validation_query, re.IGNORECASE):
            # Log warning
            log_data = {
                'message': f'Attempted to run a database modification query: {validation_query}', 'level': 'warning'}
            session.post(f'{LOGGER_URL}/log', json=log_data)
            return jsonify(valid=False, errors=['Database modification queries are not allowed'])

        with engine.connect() as connection:
            # Execute the validation query
            result = connection.execute(text(validation_query))
            # Check if the validation passed or failed
            row_count = result.rowcount

            # Log that a new form was validated
            log_data = {'message': f'Validated a form with ID: {form_id}'}
            session.post(f'{LOGGER_URL}/log', json=log_data)

            if row_count > 0:
                # Rows violating constraints found!
                return jsonify(valid=False, errors=[f'Validation failed for form {form_id}'])
            else:
                # Validation success, no rows returned
                return jsonify(valid=True)

    except Exception as error:
        # Log Error
        log_data = {'message': str(error), 'level': 'error'}
        session.post(f'{LOGGER_URL}/log', json=log_data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=os.environ.get('DEBUG'))
