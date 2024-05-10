from flask import Flask, render_template, session, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import mysql.connector.errors
from hashlib import sha256
import re
from models import User
from config import readconfig
from db import load_user, load_users, show_user, login, get_password, delete_user, change_password
from pkg import validate_password


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
    loader = load_user(UID)
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

    user = login(user_login, user_password)
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
    user = show_user()
    if user is None:
        flash('Пользователь не найден', 'danger')
        return redirect(url_for('index'))
    return render_template('showUser.html', user=user)


@app.route('/createUser', methods=["GET", "POST"])
@login_required
def createUser():
    cursor = db.connection().cursor(named_tuple=True)
    query = "SELECT role_name FROM roles"
    cursor.execute(query)
    roles = cursor.fetchall()
    cursor.close()
    if request.method == "GET":
        return render_template('createUser.html', roles=roles, selectedRole="", errors={}, user={'login': '', 'password': '', 'first_name': '', 'last_name': '', 'patronymic': '', 'role': ''})

    login = request.form.get("login")
    password = request.form.get("password")
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    patronymic = request.form.get("patronymic")
    role = "Нет" if request.form.get(
        "role") == "Выберите роль" else request.form.get("role")

    errors = {}
    if not re.fullmatch(r"[a-zA-Z0-9]{5,}", login):
        # flash('Логин должен состоять только из латинских букв и цифр и иметь длину не менее 5 символов', 'danger')
        errors["login"] = "Логин должен состоять только из латинских букв и цифр и иметь длину не менее 5 символов"
    if not login:
        errors["login"] = "Логин не может быть пустым"
        # flash('Логин не может быть пустым', 'danger')
    if not re.fullmatch(r"^(?=.+[a-zа-я])(?=.+[A-ZА-Я])(?=.*\d)(?!.*\s)[a-zA-Zа-яА-Я\d~!?@#$%^&*_\-+()\[\]{}><\\/|\"\'.,:;]{8,128}$", password):
        # flash(
        #     'Пароль не сответствует требованиям: не менее 8 символов; не более 128 символов; как минимум одна заглавная и одна строчная буква; только латинские или кириллические буквы; как минимум одна цифра; только арабские цифры; без пробелов; Другие допустимые символы:~ ! ? @ # $ % ^ & * _ - + ( ) [ ] { } > < / \ | \" \' . , : ;', 'danger')
        errors[
            "password"] = "Пароль не сответствует требованиям: не менее 8 символов; не более 128 символов; как минимум одна заглавная и одна строчная буква; только латинские или кириллические буквы; как минимум одна цифра; только арабские цифры; без пробелов; Другие допустимые символы:~ ! ? @ # $ % ^ & * _ - + ( ) [ ] { } > < / \ | \" \' . , : ;"
    if not password:
        # flash('Пароль не может быть пустым', 'danger')
        errors["password"] = "Пароль не может быть пустым"
    if not last_name:
        # flash('Фамилия не может быть пустой', 'danger')
        errors["last_name"] = "Фамилия не может быть пустой"
    if not first_name:
        # flash('Имя не может быть пустым', 'danger')
        errors["first_name"] = "Имя не может быть пустым"
    if errors:
        return render_template('createUser.html', roles=roles, selectedRole=role, errors=errors, user={'login': login, 'password': password, 'first_name': first_name, 'last_name': last_name, 'patronymic': patronymic, 'role': role})

    cursor = db.connection().cursor(named_tuple=True)

    query = "SELECT id FROM `roles` WHERE `role_name` = %s"
    values = (role,)
    try:
        cursor.execute(query, values)
        roleId = cursor.fetchone().id
    except Exception as e:
        flash(e, 'danger')
        return render_template('createUser.html', roles=roles, selectedRole=role, errors={}, user={'login': login, 'password': password, 'first_name': first_name, 'last_name': last_name, 'patronymic': patronymic, 'role': role})

    query = "INSERT INTO `users` (`login`, `password_hash`, `first_name`, `last_name`, `patronymic`, `role_id`) \
            VALUES (%s, SHA2(%s, 256), %s, %s, %s, %s)"
    values = (login, password, first_name, last_name, patronymic, roleId)
    try:
        cursor.execute(query, values)
        db.connection().commit()
        cursor.close()
        flash('Пользователь успешно создан', 'success')
        return redirect(url_for('index'))
    except mysql.connector.errors.IntegrityError as e:
        cursor.close()
        flash(f"Логин `{login}` уже занят", 'danger')
        return render_template('createUser.html', roles=roles, selectedRole=role, errors={}, user={'login': login, 'password': password, 'first_name': first_name, 'last_name': last_name, 'patronymic': patronymic, 'role': role})
    except Exception as e:
        cursor.close()
        flash(e, 'danger')
        return render_template('createUser.html', roles=roles, selectedRole=role, errors={}, user={'login': login, 'password': password, 'first_name': first_name, 'last_name': last_name, 'patronymic': patronymic, 'role': role})


@app.route('/editUser/<int:UID>', methods=["GET", "POST"])
@login_required
def editUser(UID: int):
    cursor = db.connection().cursor(named_tuple=True)

    query = "SELECT * FROM `users` WHERE `id` = %s"
    values = (UID,)
    cursor.execute(query, values)
    user = cursor.fetchone()

    query = "SELECT role_name FROM `roles`"
    cursor.execute(query)
    roles = cursor.fetchall()

    query = "SELECT role_name FROM `roles` WHERE `id` = %s"
    cursor.execute(query, (user.role_id,))
    selectedRole = cursor.fetchone()

    if request.method == "GET":
        return render_template('editUser.html', roles=roles, selectedRole=selectedRole.role_name, errors={}, user=user)

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

    query = "UPDATE users \
            SET first_name = %s, last_name = %s, patronymic = %s, role_id = (SELECT id FROM roles WHERE role_name = %s) \
            WHERE id = %s; "
    values = (first_name, last_name, patronymic, role, UID)
    try:
        cursor.execute(query, values)
        db.connection().commit()
        cursor.close()
        flash('Пользователь успешно отредактирован', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        flash(e, 'danger')
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

    flash_msg, flash_status, errors = validate_password(oldPasswordSHA2, newPassword, newPasswordSHA2, repeatPassword, password_hash)

    if errors:
        flash(flash_msg, flash_status)
        return render_template('changePassword.html', errors=errors)


    flash_msg, flash_status = change_password(newPassword, current_user)

    if flash_status == 'success':
        flash(flash_msg, flash_status)
        return redirect(url_for('index'))

    if flash_status == 'danger':
        flash(flash_msg, flash_status)
        return render_template('changePassword.html', errors={})
