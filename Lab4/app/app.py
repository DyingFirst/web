from flask import Flask, render_template, session, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from hashlib import sha256
from models import User
from config import readconfig
from db import load_user_db, load_users, show_user, get_user_from_db, get_password, delete_user, change_password, any_from_users_by_ID, roles_name, role_name_by_ID, edit_user, get_role_names,create_new_user
from pkg import validate_password, validate_new_user


app = Flask(__name__)
cfg = readconfig()
app.config['SECRET_KEY'] = cfg['key']

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = 'login'
login_manager.login_message = 'Для доступа к данной странице необходимо пройти аутентификацию'
login_manager.login_message_category = "warning"



@login_manager.user_loader
def load_user(UID):
    loader = load_user_db(UID)
    return loader

@app.route('/')
def index():
    users = load_users()
    return render_template('index.html', users=users)


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    user_login = request.form['login']
    user_password = request.form['password']
    remember = request.form.get('remember') == 'on'

    user = get_user_from_db(user_login, user_password)
    if not user:
        flash('Логин или пароль введены неверно', 'danger')
        return render_template("login.html")

    login_user(User(user.id, user.login), remember=remember)
    param = request.args.get('next')
    flash('Успешный вход', 'success')
    return redirect(param or url_for('index'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/showUser/<int:UID>', methods=["GET", "POST"])
def showUser(UID: int):
    user = show_user(UID)
    if user is None:
        flash('Пользователь не найден', 'danger')
        return redirect(url_for('index'))
    return render_template('showUser.html', user=user)


@app.route('/createUser', methods=["GET", "POST"])
@login_required
def createUser():

    roles = get_role_names()

    if request.method == "GET":
        return render_template('createUser.html', roles=roles, selectedRole="", errors={}, user={'login': '', 'password': '', 'first_name': '', 'last_name': '', 'patronymic': '', 'role': ''})

    login = request.form.get("login")
    password = request.form.get("password")
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    patronymic = request.form.get("patronymic")
    role = "Нет" if request.form.get(
        "role") == "Выберите роль" else request.form.get("role")

    errors = validate_new_user(login, password, first_name, last_name)

    if errors:
        return render_template('createUser.html', roles=roles, selectedRole=role, errors=errors, user={'login': login, 'password': password, 'first_name': first_name, 'last_name': last_name, 'patronymic': patronymic, 'role': role})

    flash_msg, flash_status = create_new_user(login, password, first_name, last_name, patronymic, role)
    if flash_status == 'success':
        flash(flash_msg, flash_status)
        return redirect(url_for('index'))
    if flash_status == 'danger':
        flash(flash_msg, flash_status)
        return render_template('createUser.html', roles=roles, selectedRole=role, errors={}, user={'login': login, 'password': password, 'first_name': first_name, 'last_name': last_name, 'patronymic': patronymic, 'role': role})


@app.route('/editUser/<int:UID>', methods=["GET", "POST"])
@login_required
def editUser(UID: int):

    user = any_from_users_by_ID(UID)
    roles = roles_name()
    selected_role = role_name_by_ID(user)

    if request.method == "GET":
        return render_template('editUser.html', roles=roles, selectedRole=selected_role.role_name, errors={}, user=user)

    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    patronymic = request.form.get("patronymic")
    role = "Нет" if request.form.get(
        "role") == "Выберите роль" else request.form.get("role")

    errors = {}
    if not first_name:
        # flash('Имя не может быть пустым', 'danger')
        errors["first_name"] = "Имя не может быть пустым"
    if not last_name:
        # flash('Фамилия не может быть пустой', 'danger')
        errors["last_name"] = "Фамилия не может быть пустой"
    if errors:
        return render_template('createUser.html', roles=roles, selectedRole=role, errors=errors, user={'first_name': first_name, 'last_name': last_name, 'patronymic': patronymic, 'role': role})

    flash_msg, flash_status = edit_user(first_name, last_name, patronymic, role, UID)
    if flash_status == 'success':
        flash(flash_msg, flash_status)
        return redirect(url_for('index'))
    if flash_status == 'danger':
        flash(flash_msg, flash_status)
        return render_template('editUser.html', roles=roles, selectedRole=role, errors={}, user={'first_name': first_name, 'last_name': last_name, 'patronymic': patronymic, 'role': role})


@app.route('/deleteUser/<int:UID>')
@login_required
def deleteUser(UID: int):
    error_msg, status = delete_user(UID)
    flash(error_msg, status)
    return redirect(url_for('index'))


@app.route('/changePassword', methods=["GET", "POST"])
@login_required
def changePassword():
    if request.method == "GET":
        return render_template('changePassword.html', user={}, errors={})

    oldPassword = request.form.get("oldPassword")
    newPassword = request.form.get("newPassword")
    repeatPassword = request.form.get("repeatPassword")

    old = sha256()
    old.update(oldPassword.encode('UTF-8'))
    oldPasswordSHA2 = old.hexdigest()

    new = sha256()
    new.update(newPassword.encode('UTF-8'))
    newPasswordSHA2 = new.hexdigest()

    password_hash, flash_msg, flash_status = get_password(current_user)
    if flash_status == 'danger':
        return render_template('changePassword.html', errors={})

    flash_msg, errors = validate_password(oldPasswordSHA2, newPassword, newPasswordSHA2, repeatPassword, password_hash)

    if flash_msg:
        flash(flash_msg, 'danger')
        return render_template('changePassword.html', errors=errors)

    if errors:
        return render_template('changePassword.html', errors=errors)


    flash_msg, flash_status = change_password(newPassword, current_user)

    if flash_status == 'success':
        flash(flash_msg, flash_status)
        return redirect(url_for('index'))

    if flash_status == 'danger':
        return render_template('changePassword.html', errors={})
