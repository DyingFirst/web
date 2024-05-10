from flask import Flask, render_template, session, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

import re

app = Flask(__name__)

application = app

app.config.from_pyfile('config.py')

login_manager = LoginManager()

login_manager.login_view = 'login'
login_manager.login_message = 'Для доступа к данной странице необходимо пройти аутентификацию'
login_manager.login_message_category = "warning"


class User(UserMixin):
    def __init__(self, user_id, login, password):
        self.id = user_id
        self.login = login
        self.password = password


def userList():
    return [
        {
            "id": 1,
            "login": "user",
            "password": "qwerty"
        },
        {
            "id": 2,
            "login": "admin",
            "password": "admin"
        },
    ]


@login_manager.user_loader
def load_user(user_id):
    for user in userList():
        if int(user_id) == user['id']:
            return User(user['id'], user['login'], user["password"])
    return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/counter')
@login_required
def counter():
    if 'visits' in session:
        session['visits'] += 1
    else:
        session['visits'] = 1
    return render_template('counter.html')


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    login = request.form['login']
    password = request.form['password']
    remember = request.form.get('remember') == 'on'
    for user in userList():
        if login == user["login"] and password == user["password"]:
            login_user(User(user['id'], user['login'],
                       user['password']), remember=remember)
            param = request.args.get('next')
            flash('Успешный вход', 'success')
            return redirect(param or url_for('index'))
    flash('Логин или пароль введены неверно', 'danger')
    return render_template("login.html")


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/secret')
@login_required
def secret():
    return render_template('secret.html')

if __name__ == "__main__":
    login_manager.init_app(app)
    application.run(debug=True)
