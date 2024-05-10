from models import User
from config import readconfig
from connector_db import MySQL

cfg = readconfig()
db = MySQL(cfg)


def load_user(UID):
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

def login(login, password):
    cursor = db.connection().cursor(named_tuple=True)
    query = "SELECT * FROM `users` \
                WHERE `login` = %s AND `password_hash` = SHA2(%s, 256)"
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
        flash_msg = ('Пароль успешно изменен', 'success')
        return flash_msg
    except Exception as e:
        cursor.close()
        flash_msg = (str(e), 'danger')
        return flash_msg
