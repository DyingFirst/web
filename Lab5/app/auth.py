from flask import (
    render_template,
    url_for,
    request,
    redirect,
    flash,
    Blueprint,
)
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from functools import wraps
from app import db

bp_auth = Blueprint("auth", __name__, url_prefix="/auth")


ADMIN_ROLE_ID = 1
USER_ROLE_ID = 2
NO_ROLE_ID = 4


def check_rights(rule):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # user = load_user(kwargs.get("user_id", None))
            if not current_user.is_authenticated:
                flash(
                    "Для доступа к данной странице необходимо пройти аутентификацию",
                    "warning",
                )
                return redirect(url_for("index"))
            if current_user.can(rule):
                return f(*args, **kwargs)
            flash("Permission denied", "warning")
            return redirect(url_for("index"))

        return decorated_function

    return decorator


def init_login_manager(app):
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"
    login_manager.login_message = (
        "Для доступа к данной странице необходимо пройти аутентификацию"
    )
    login_manager.login_message_category = "warning"
    login_manager.user_loader(load_user)


class User(UserMixin):
    def __init__(self, user_id, login, role_id):
        self.id = user_id
        self.login = login
        self.role_id = role_id

    def is_admin(self):
        return self.role_id == ADMIN_ROLE_ID

    def can(self, action):
        match action:
            case "createUser" | "deleteUser":
                return self.role_id == ADMIN_ROLE_ID
            case "editUser" | "showUser":
                if self.role_id == ADMIN_ROLE_ID:
                    return True
                return str(current_user.id) == request.path.split("/")[-1]
            case "showVisitLogs" | "showPageLogs" | "showUserLogs":
                return True
        return False


def load_user(UID):
    cursor = db.connection().cursor(named_tuple=True)
    query = "SELECT id, login, role_id FROM users WHERE id = %s"
    cursor.execute(query, (UID,))
    user = cursor.fetchone()
    cursor.close()
    if user:
        return User(user.id, user.login, user.role_id)
    return None


@bp_auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    login = request.form["login"]
    password = request.form["password"]
    remember = request.form.get("remember") == "on"
    cursor = db.connection().cursor(named_tuple=True)
    query = "SELECT * FROM `users` \
            WHERE `login` = %s AND `password_hash` = SHA2(%s, 256)"
    cursor.execute(query, (login, password))
    user = cursor.fetchone()
    cursor.close()

    if not user:
        flash("Логин или пароль введены неверно", "danger")
        return render_template("login.html")

    login_user(User(user.id, user.login, user.role_id), remember=remember)
    param = request.args.get("next")
    flash("Успешный вход", "success")
    return redirect(param or url_for("index"))


@bp_auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))
