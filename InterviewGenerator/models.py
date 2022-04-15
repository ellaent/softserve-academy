from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()


class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    theme = db.Column(db.String())
    essence = db.Column(db.String(), nullable=False)
    answer = db.Column(db.String(), default='Free answer')
    mark = db.Column(db.Numeric(), default=10)

    def __init__(self, theme, essence, answer, mark):
        self.theme = theme
        self.essence = essence
        self.answer = answer
        self.mark = mark

    def __repr__(self):
        return '<{}.{}>'.format(self.theme, self.essence)


class QuestionSet(db.Model):
    __tablename__ = 'sets'
    # __table_args__ = {'extend_existing': True}
    # __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    questions = db.relationship("Question", secondary="questions_sets")
    level = db.Column(db.String())

    def __init__(self, name, level, questions):
        self.name = name
        self.level = level
        self.questions = questions

    def __repr__(self):
        return '{}'.format(self.name)


class QuestionsSets(db.Model):
    __tablename__ = 'questions_sets'
    # __table_args__ = {'extend_existing': True}
    # __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    set_id = db.Column(db.Integer, db.ForeignKey('sets.id'))

    question = db.relationship(Question, backref=backref("questionssets", cascade="all, delete-orphan"))
    set = db.relationship(QuestionSet, backref=backref("questionssets", cascade="all, delete-orphan"))


class QuestionMark(db.Model):
    __tablename__ = 'questionmarks'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    interview_id = db.Column(db.Integer, db.ForeignKey('interviews.id'))
    expert_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    mark = db.Column(db.Integer)


class User(UserMixin, db.Model):

    __tablename__ = 'users'
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    name = db.Column(
        db.String(100),
        nullable=False,
        unique=False
    )
    surname = db.Column(
        db.String(100),
        nullable=False,
        unique=False
    )
    email = db.Column(
        db.String(40),
        unique=True,
        nullable=False
    )
    is_recruiter = db.Column(
        db.Boolean
    )
    is_expert = db.Column(
        db.Boolean
    )
    is_admin = db.Column(
        db.Boolean
    )
    is_active = db.Column(
        db.Boolean,
        default=True,
        server_default="true",
        nullable=False
    )
    password = db.Column(
        db.String(200),
        primary_key=False,
        unique=False,
        nullable=True
	)
    created_on = db.Column(
        db.DateTime,
        index=False,
        unique=False,
        nullable=True
    )
    last_login = db.Column(
        db.DateTime,
        index=False,
        unique=False,
        nullable=True
    )

    def set_password(self, password):
        self.password = generate_password_hash(
            password,
            method='sha256'
        )

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '{} {}'.format(self.name, self.surname)


class Interview(db.Model):
    __tablename__ = 'interviews'

    id = db.Column(db.Integer,
                   primary_key=True)
    assignee = db.Column(db.String(),
                         nullable=False)
    position = db.Column(db.String(),
                         nullable=True)
    max_score = db.Column(db.Integer(),
                      nullable=True)
    score = db.Column(db.Integer(),
                      nullable=True)
    is_conducted = db.Column(
        db.Boolean,
        default=False,
        server_default="false",
        nullable=False
    )
    questions = db.relationship("Question", secondary="questions_interviews")
    sets = db.relationship("QuestionSet", secondary="sets_interviews")
    experts = db.relationship("User", secondary="experts_interviews")

    recruiter_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, assignee, position, experts):
        self.assignee = assignee
        self.position = position
        self.experts = experts

    def __repr__(self):
        return '{} for {}'.format(self.id, self.assignee)


class QuestionsInterviews(db.Model):
    __tablename__ = 'questions_interviews'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    interview_id = db.Column(db.Integer, db.ForeignKey('interviews.id'))

    question = db.relationship(Question, backref=backref("questionsinterviews", cascade="all, delete-orphan"))
    interview = db.relationship(Interview, backref=backref("questionsinterviews", cascade="all, delete-orphan"))


class SetsInterviews(db.Model):
    __tablename__ = 'sets_interviews'

    id = db.Column(db.Integer, primary_key=True)
    set_id = db.Column(db.Integer, db.ForeignKey('sets.id'))
    interview_id = db.Column(db.Integer, db.ForeignKey('interviews.id'))

    set = db.relationship(QuestionSet, backref=backref("setsinterviews", cascade="all, delete-orphan"))
    interview = db.relationship(Interview, backref=backref("setsinterviews", cascade="all, delete-orphan"))


class ExpertsInterviews(db.Model):
    __tablename__ = 'experts_interviews'

    id = db.Column(db.Integer, primary_key=True)
    expert_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    interview_id = db.Column(db.Integer, db.ForeignKey('interviews.id'))

    expert = db.relationship(User, backref=backref("expertsinterviews", cascade="all, delete-orphan"))
    interview = db.relationship(Interview, backref=backref("expertsinterviews", cascade="all, delete-orphan"))

