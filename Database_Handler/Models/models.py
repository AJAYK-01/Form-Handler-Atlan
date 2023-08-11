from sqlalchemy import text
from sqlalchemy import inspect
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Form(db.Model):
    __tablename__ = 'form'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    created_at = db.Column(db.DateTime)


class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey('form.id'))
    form = db.relationship('Form', backref='questions')
    question_text = db.Column(db.String)
    question_type = db.Column(db.String)


class Response(db.Model):
    __tablename__ = 'response'
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey('form.id'))
    form = db.relationship('Form', backref='responses')
    email = db.Column(db.String)
    submitted_at = db.Column(db.DateTime)


class Answer(db.Model):
    __tablename__ = 'answer'
    id = db.Column(db.Integer, primary_key=True)
    response_id = db.Column(db.Integer, db.ForeignKey('response.id'))
    response = db.relationship('Response', backref='answers')
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    question = db.relationship('Question', backref='answers')
    answer_text = db.Column(db.String)
    updated_at = db.Column(db.DateTime)


def init_db():
    inspector = inspect(db.engine)

    # Check if the tables exist
    if not inspector.has_table('form'):
        Form.__table__.create(db.engine)
    if not inspector.has_table('question'):
        Question.__table__.create(db.engine)
    if not inspector.has_table('response'):
        Response.__table__.create(db.engine)
    if not inspector.has_table('answer'):
        Answer.__table__.create(db.engine)
