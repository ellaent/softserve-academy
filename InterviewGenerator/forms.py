from wtforms_sqlalchemy.fields import QuerySelectMultipleField
from wtforms import Form, StringField, PasswordField, SubmitField, RadioField, DecimalField, SelectField, validators
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    Optional
)


class QuestionsCreateForm(Form):
    theme = StringField('Theme', [validators.Length(min=2)])
    essence = StringField('Essence', [validators.Length(min=4)])
    answer = StringField('Expected Answer',)
    mark = DecimalField('Max Mark', validators=[validators.NumberRange(min=1, max=10)])


class QuestionSearchForm(Form):
    search = StringField('')


class QuestionSetCreateForm(Form):
    name = StringField('Name', [validators.Length(min=2)])
    questions = QuerySelectMultipleField('Questions', allow_blank=True,)
    level = SelectField("Level: ", choices=[
        ("easy", "easy"),
        ("medium", "medium"),
        ("hard", "hard")])


class SignupForm(Form):
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=6, message='Select a stronger password.')
        ]
    )
    confirm = PasswordField(
        'Confirm Your Password',
        validators=[
            DataRequired(),
            EqualTo('password', message='Passwords must match.')
        ]
    )
    submit = SubmitField('Register')


class LoginForm(Form):
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(message='Enter a valid email.')
        ]
    )
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')


class AddUserForm(Form):
    name = StringField(
        'Name',
        validators=[DataRequired()]
    )
    surname = StringField(
        'Surname',
        validators=[DataRequired()]
    )
    email = StringField(
        'Email',
        validators=[
            Length(min=6),
            Email(message='Enter a valid email.'),
            DataRequired()
        ]
    )
    role = RadioField('Role', choices=[('recruiter','recruiter'),('expert','expert')], validators=[DataRequired()])
    # admin = widgets.CheckboxInput()
    submit = SubmitField('Register')
