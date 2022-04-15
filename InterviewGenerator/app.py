from flask import Flask, flash, redirect, url_for
from flask_migrate import Migrate
import click
from flask.cli import AppGroup
from flask_login import LoginManager
from flask_mail import Mail, Message

from routes import helper, SECRET_KEY
from models import db, Question, QuestionSet, QuestionsSets, User

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://mur:mur@localhost/interviewgenerator"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = SECRET_KEY
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'mur@mur.com'
app.config['MAIL_PASSWORD'] = 'mur_secret'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEFAULT_SENDER'] = 'mur@mur.com'

login_manager = LoginManager()
mail = Mail(app)

with app.app_context():
    db.init_app(app)
    migrate = Migrate(app, db)
    login_manager.init_app(app)

app.register_blueprint(helper)

user_cli = AppGroup('user')


@user_cli.command('create-super')
# @click.argument()
def create_user():
    user = User(
        name="Eleonora",
        surname="Entina",
        email="mur@mur.com",
        is_admin=True,
    )
    user.set_password('1234')
    db.session.add(user)
    db.session.commit()

app.cli.add_command(user_cli)


@login_manager.user_loader
def load_user(user_id):
    if user_id is not None:
        return User.query.get(user_id)
    return None


@login_manager.unauthorized_handler
def unauthorized():
    flash('You must be logged in to view that page.')
    return redirect(url_for('helper.login'))


if __name__ == '__main__':
    app.run(debug=True)







