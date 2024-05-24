from models import User
from config import readconfig
from connector_db import MySQL
import mysql.connector.errors

cfg = readconfig()
db = MySQL(cfg)


def load_user_db(UID):
    cursor = db.connection().cursor(named_tuple=True)
    query = 'SELECT id, login FROM users WHERE id = %s'
    cursor.execute(query, (UID,))
    user = cursor.fetchone()
    cursor.close()
    if user:
        return User(user.id, user.login)
    return None


def load_users():
    cursor = db.connection().cursor(named_tuple=True)
    query = "SELECT users.id, users.login, users.first_name, users.last_name, users.patronymic, roles.role_name FROM `users` \
            JOIN roles on users.role_id = roles.id \
            ORDER BY users.id"
    cursor.execute(query)
    users = cursor.fetchall()
    cursor.close()
    return users


def show_user(UID):
    cursor = db.connection().cursor(named_tuple=True)
    query = "SELECT users.id, users.login, users.first_name, users.last_name, users.patronymic, roles.role_name FROM `users` \
                JOIN roles on users.role_id = roles.id \
                WHERE users.id = %s"
    cursor.execute(query, (UID,))
    user = cursor.fetchone()
    cursor.close()
    return user


def get_user_from_db(login, password):
    cursor = db.connection().cursor(named_tuple=True)
    query = "SELECT * FROM `users` WHERE `login` = %s AND `password_hash` = SHA2(%s, 256)"
    cursor.execute(query, (login, password))
    user = cursor.fetchone()
    cursor.close()
    return user


def get_password(current_user):
    cursor = db.connection().cursor(named_tuple=True)
    try:
        query = "SELECT password_hash FROM `users` WHERE `id` = %s"
        values = (current_user.id,)
        cursor.execute(query, values)
        password_hash = cursor.fetchone()
        return password_hash, None
    except Exception as e:
        flash_msg = (str(e), 'danger')
        return None, flash_msg


def delete_user(UID):
    cursor = db.connection().cursor()
    try:
        query = "DELETE FROM `users` WHERE `id` = %s;"
        values = (UID,)
        cursor.execute(query, values)
        db.connection().commit()
        flash_msg = ('Пользователь успешно удален', 'success')
        return flash_msg
    except Exception as e:
        flash_msg = (str(e), 'danger')
        return flash_msg
    finally:
        cursor.close()


def change_password(newPassword, current_user):
    query = "UPDATE `users` SET `password_hash` = SHA2(%s, 256) WHERE `id` = %s"
    values = (newPassword, current_user.id)
    cursor = db.connection().cursor()
    try:
        cursor.execute(query, values)
        db.connection().commit()
        cursor.close()
        flash_msg, flash_status = ('Пароль успешно изменен', 'success')
        return flash_msg
    except Exception as e:
        cursor.close()
        flash_msg, flash_status = (str(e), 'danger')
        return flash_msg, flash_status


def any_from_users_by_ID(UID):
    cursor = db.connection().cursor(named_tuple=True)

    query = "SELECT * FROM `users` WHERE `id` = %s"
    values = (UID,)
    cursor.execute(query, values)
    user = cursor.fetchone()

    return user


def roles_name():
    cursor = db.connection().cursor(named_tuple=True)

    query = "SELECT role_name FROM `roles`"
    cursor.execute(query)
    roles = cursor.fetchall()
    return roles


def role_name_by_ID(user):
    cursor = db.connection().cursor(named_tuple=True)

    query = "SELECT role_name FROM `roles` WHERE `id` = %s"
    cursor.execute(query, (user.role_id,))
    selectedRole = cursor.fetchone()
    return selectedRole


def edit_user(first_name, last_name, patronymic, role, UID):
    cursor = db.connection().cursor(named_tuple=True)

    query = "UPDATE users \
                SET first_name = %s, last_name = %s, patronymic = %s, role_id = (SELECT id FROM roles WHERE role_name = %s) \
                WHERE id = %s; "
    values = (first_name, last_name, patronymic, role, UID)
    try:
        cursor.execute(query, values)
        db.connection().commit()
        cursor.close()
        flash_msg = ('Пользователь успешно отредактирован', 'success')
        return flash_msg
    except Exception as e:
        flash_msg = (str(e), 'danger')
        return flash_msg


def get_role_names():
    cursor = db.connection().cursor(named_tuple=True)
    query = "SELECT role_name FROM roles"
    cursor.execute(query)
    roles = cursor.fetchall()
    cursor.close()
    return roles


def create_new_user(login, password, first_name, last_name, patronymic, role):
    cursor = db.connection().cursor(named_tuple=True)

    query = "SELECT id FROM `roles` WHERE `role_name` = %s"
    values = (role,)
    try:
        cursor.execute(query, values)
        roleId = cursor.fetchone().id
    except Exception as e:
        flash_msg = (str(e), 'danger')

    query = "INSERT INTO `users` (`login`, `password_hash`, `first_name`, `last_name`, `patronymic`, `role_id`) \
            VALUES (%s, SHA2(%s, 256), %s, %s, %s, %s)"
    values = (login, password, first_name, last_name, patronymic, roleId)
    try:
        cursor.execute(query, values)
        db.connection().commit()
        cursor.close()
        flash_msg = ('Пользователь успешно создан', 'success')
        return flash_msg
    except mysql.connector.errors.IntegrityError as e:
        cursor.close()
        flash_msg = (f"Логин `{login}` уже занят", 'danger')
        return flash_msg
    except Exception as e:
        cursor.close()
        flash_msg = (str(e), 'danger')
        return flash_msg
