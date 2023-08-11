from flask import Flask, request, jsonify
from Models.models import db, init_db, Form, Question, Response, Answer

import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

db.init_app(app)

# Call the init_db function before running the app
with app.app_context():
    init_db()


# API route to create forms
@app.route('/create-form', methods=['POST'], strict_slashes=False)
def create_form():
    data = request.json  # Assuming JSON format

    title = data.get('title')
    questions = data.get('questions')

    # Create a new form
    form = Form(title=title)
    db.session.add(form)
    db.session.commit()

    # Add questions to the form
    for question_data in questions:
        question_text = question_data.get('question_text')
        question_type = question_data.get('question_type')
        question = Question(
            form=form, question_text=question_text, question_type=question_type)
        db.session.add(question)

    db.session.commit()

    return jsonify(message='Form created successfully')


# API route to handle submitting responses
@app.route('/submit-response', methods=['POST'], strict_slashes=False)
def submit_response():
    data = request.json  # Assuming JSON format

    form_id = data.get('form_id')
    email = data.get('email')
    answers = data.get('answers')

    # Create a new response
    response = Response(form_id=form_id, email=email)
    db.session.add(response)
    db.session.commit()

    # Add answers to the response
    for answer_data in answers:
        question_id = answer_data.get('question_id')
        answer_text = answer_data.get('answer_text')
        answer = Answer(response=response,
                        question_id=question_id, answer_text=answer_text)
        db.session.add(answer)

    db.session.commit()

    return jsonify(message='Response submit successfully')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=(os.environ.get('DEBUG')))
