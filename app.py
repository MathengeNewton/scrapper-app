from flask import Flask, render_template, redirect, url_for, session
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, length
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import requests


app = Flask(__name__)
app.config['SECRET_KEY'] = "secretkey"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:mathenge,./1998@localhost/mainapp'
Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class userinfo(UserMixin, db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return userinfo.query.get(int(user_id))


class LoginForm(FlaskForm):

    email = StringField('email', validators=[
        InputRequired(), length(min=10, max=20)])
    password = PasswordField('password', validators=[
                             InputRequired(), length(min=8, max=80)])


class Registration(FlaskForm):
    name = StringField('name', validators=[
                       InputRequired(), length(min=6, max=20)])
    email = StringField('email', validators=[
                        InputRequired(), length(min=10, max=20)])
    password = PasswordField('password', validators=[
                             InputRequired(), length(min=8, max=80)])


@app.route('/')
def index():
    form = LoginForm()
    return render_template('index.html', form=form)


# @app.route('/request')
# def request():
#     res = requests.get('https://https://www.crafted.co.ke/')
#     return res.headers


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        account = userinfo.query.filter_by(email=form.email.data).first()
        if account:
            if account.password == form.password.data:
                session['user'] = account.name
                return redirect(url_for('dashboard'))
        else:
            return '<h1>Invalid user or password</h1>'

    else:
        return render_template('index.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = Registration()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(
            form.password.data, method='sha256')
        new_user = userinfo(name=form.name.data,
                            email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return render_template('index.html')

    else:
        return render_template('register.html', form=form)


@app.route('/mydash')
def dashboard():
    if 'user' in session:
        user = session['user']
        return render_template('mydash.html', name=user)
    else:
        return redirect(url_for('login'))


@app.route('/mydash/flikr')
def flikr():
    DATA = {'Key': '95c5354ee0e9a1f187a292ad30c922f8',
            'Secret': 'a4120895f35b5c97'}
    UPLOAD_URL = 'https://up.flickr.com/services/upload/'
    SECRET_KEY = 'fd44b95d5f2841cc'
    API_KEY = '9d6ba648cd295dd4e605e7f814bb69e5'
    session['platform'] = 'flikr'
    platform = session['platform']
    user = session['user']
    name = user + "'s"
    return render_template('/flikr.html', name=name, platform=platform)


if __name__ == "__main__":
    app.run(debug=True)
