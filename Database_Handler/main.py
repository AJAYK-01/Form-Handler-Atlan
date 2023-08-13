from flask import Flask, request, jsonify
from Models.models import db, init_db, Form, Question, Response, Answer

from requests import Session
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

db.init_app(app)

# helps identify the microservice during logging
session = Session()
session.headers.update({'X-Docker-Domain': 'db_handler'})
LOGGER_URL = os.environ.get('LOGGER_URL')

# Call the init_db function before running the app
with app.app_context():
    init_db()


@app.route('/create-form', methods=['POST'], strict_slashes=False)
def create_form():
    ''' API route to create forms '''
    try:
        data = request.json  # Assuming JSON format

        title = data['title']
        questions = data['questions']

        # Create a new form
        form = Form(title=title)
        db.session.add(form)
        db.session.commit()

        # Add questions to the form
        for question_data in questions:
            question_text = question_data['question_text']
            question_type = question_data['question_type']
            question = Question(
                form=form, question_text=question_text, question_type=question_type)
            db.session.add(question)

        db.session.commit()

        # Log that a new form was created
        log_data = {'message': f'Created new form with ID: {form.id}'}
        session.post(f'{LOGGER_URL}/log', json=log_data)

        return jsonify(message='Form created successfully')

    except Exception as error:
        # Log Error
        log_data = {'message': str(error), 'level': 'error'}
        session.post(f'{LOGGER_URL}/log', json=log_data)

        return jsonify(message='Error occurred: check logs for details'), 500


@app.route('/submit-response', methods=['POST'], strict_slashes=False)
def submit_response():
    ''' API route to handle submitting responses '''
    try:
        data = request.json  # Assuming JSON format

        form_id = data['form_id']
        email = data['email']
        answers = data['answers']

        # Create a new response
        response = Response(form_id=form_id, email=email)
        db.session.add(response)
        db.session.commit()

        # Add answers to the response
        for answer_data in answers:
            question_id = answer_data['question_id']
            answer_text = answer_data['answer_text']
            answer = Answer(response=response,
                            question_id=question_id, answer_text=answer_text)
            db.session.add(answer)

        db.session.commit()

        # Log that a new response was submiteed
        log_data = {'message': f'Submitted new response with ID: {response.id}'}
        session.post(f'{LOGGER_URL}/log', json=log_data)

        return jsonify(message='Response submit successfully')

    except Exception as error:
        # Log Error
        log_data = {'message': str(error), 'level': 'error'}
        session.post(f'{LOGGER_URL}/log', json=log_data)

        return jsonify(message='Error occurred: check logs for details'), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=os.environ.get('DEBUG'))
