from flask import Flask, render_template, redirect, url_for, session
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, DateField
from wtforms.validators import InputRequired, Email, length
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import requests


app = Flask(__name__)
app.config.from_pyfile('config.py')
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


class employees(UserMixin, db.Model):
    id = db.Column(db.Integer, nullable=False,
                   primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False, unique=True)
    department = db.Column(db.String(80), nullable=False)


class leaves(UserMixin, db.Model):
    id = db.Column(db.Integer, nullable=False, autoincrement=True,
                   primary_key=True)
    emp_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    category = db.Column(db.String, nullable=False)


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


class register_leave(FlaskForm):
    startdate = DateField('startdate', validators=[InputRequired()])
    enddate = DateField('enddate', validators=[InputRequired()])
    category = StringField('category', validators=[InputRequired()])


@login_manager.user_loader
def load_user(id):
    return userinfo.query.get(int(id))


@app.route('/')
def index():
    form = LoginForm()
    return render_template('index.html', form=form)


@app.route('/leaves')
def leaves():
    user = session['user']
    return render_template('leavesdash.html', user=user)


@app.route('/long_leave')
def long_leave():
    user = session['user']
    return render_template('long_leave.html', user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        account = userinfo.query.filter_by(email=form.email.data).first()
        print(account.id)
        if account:
            newpass = generate_password_hash(
                form.password.data, method='sha256')
            if form.password.data:
                session['user'] = account.name
                session['id'] = account.id
                return redirect(url_for('dashboard'))
        else:
            return '<h1>Invalid user or password</h1>'

    else:
        return render_template('index.html', form=form)

    return redirect(url_for('login'))


@app.route('/emp-employee')
def empLogin():
    return "<h1>hello</h1>"


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
        return render_template('index.html', form=form)

    else:
        return render_template('register.html', form=form)


@app.route('/mydash')
def dashboard():
    form = LoginForm()
    if 'user' in session:
        user = session['user']
        return render_template('mydash.html', user=user)
    else:
        return redirect(url_for('login'))


@app.route('/mydash/flikr')
def flikr():
    if 'user' in session:
        if 'platform' in session:
            platform = session['platform']
            name = session['user']
            return render_template('flikr.html', name=name, platform=platform)
        elif 'platform' == 'flikr' in session:
            return render_template('flikr.html', name=name, platform=platform)
        else:
            session['platform'] = 'flikr'
            platform = session['platform']
            name = session['user']
            return render_template('flikr.html', name=name, platform=platform)

    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    if 'platform' in session:
        session.pop('platform')
        return redirect(url_for('dashboard'))
    return redirect(url_for('dashboard'))


@app.route('/logout_all')
def logoutall():
    session.pop('user')
    return redirect(url_for('login'))


@app.route('/mydash/github')
def github():
    if 'user' in session:
        if 'platform' in session:
            platform = session['platform']
            name = session['user']
            return render_template('github.html', name=name, platform=platform)
        elif 'platform' == 'github' in session:
            return render_template('github.html', name=name, platform=platform)
        else:
            session['platform'] = 'github'
            platform = session['platform']
            name = session['user']
            return render_template('github.html', name=name, platform=platform)

    return redirect(url_for('login'))


@app.route('/add')
def new_platform():
    return '<h1>loged out</h1>'

    def __init__():
        return f"<p>helloworld</p>"


@app.route('/myleaves')
def myleaves():
    user = session['user']
    return render_template('myleaves.html', user=user)


@app.route('/request/leaves')
def requestleave():
    form = register_leave()
    user = session['user']
    return render_template('requestleave.html', user=user, form=form)


@app.route('/shortleave')
def registered_leave():
    return f'hello world'


@app.route('/shortleave')
def shortleave():
    return render_template(url_for('registered_leave'))


@app.route('/add-leave', methods=['POST'])
def add_leave():
    if 'user' in session:
        form = register_leave()
        my_id = session['id']
        if form.validate_on_submit():
            # new_leave = leaves(emp_id=my_id, start_date=form.startdate.data,
            #                    end_date=form.enddate.data, category=form.category.data)

            print(form.startdate.data)
        else:
            return f'success -1'
            # db.session.add(new_leave)
            # db.session.commit()
    else:
        return f'problem 1'
    return f'problem 2'


if __name__ == "__main__":
    app.run()
