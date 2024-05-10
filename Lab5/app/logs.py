from flask import render_template, request, Blueprint, send_file  # noqa
from flask_login import login_required, current_user  # noqa
from app import db  # noqa
import math  # noqa
import csv  # noqa
from io import BytesIO  # noqa
from auth import check_rights

bp_logs = Blueprint("logs", __name__, url_prefix="/logs")
PER_PAGE = 15


@bp_logs.route("/visitLogs")
@check_rights("showVisitLogs")
@login_required
def visitLogs():
    cursor = db.connection().cursor(named_tuple=True)
    query = """SELECT CONCAT(users.last_name, ' ', users.first_name, ' ', users.patronymic) as bio,
               visit_logs.path as path,
               visit_logs.created_at as created_at,
               users.login as login
               FROM visit_logs
               LEFT JOIN users on visit_logs.user_id = users.id"""
    cursor.execute(query)
    logs = cursor.fetchall()
    logs.sort(key=lambda x: x[2], reverse=True)
    logs = list(
        filter(lambda x: current_user.is_admin() or x[3] == current_user.login, logs)
    )
    cursor.close()
    offset = (int(request.args.get("page", 1)) - 1) * PER_PAGE
    return render_template(
        "visitLogs.html",
        logs=logs[offset : offset + PER_PAGE],
        lastPage=len(logs) // PER_PAGE + 1,
    )


@bp_logs.route("/pageLogs")
@check_rights("showPageLogs")
@login_required
def pageLogs():
    cursor = db.connection().cursor(named_tuple=True)

    if current_user.is_admin():
        query = """SELECT visit_logs.path as path,
                   COUNT(*) as count
                   FROM visit_logs
                   LEFT JOIN users on visit_logs.user_id = users.id
                   GROUP BY path"""
        cursor.execute(query)
    else:
        query = """SELECT visit_logs.path as path,
                   COUNT(*) as count
                   FROM visit_logs
                   LEFT JOIN users on visit_logs.user_id = users.id
                   WHERE users.login = %s
                   GROUP BY path"""

        cursor.execute(query, (current_user.login,))

    logs = cursor.fetchall()
    logs.sort(key=lambda x: x[1], reverse=True)
    cursor.close()
    offset = (int(request.args.get("page", 1)) - 1) * PER_PAGE
    return render_template(
        "pageLogs.html",
        logs=logs[offset : offset + PER_PAGE],
        lastPage=len(logs) // PER_PAGE + 1,
    )


@bp_logs.route("/userLogs")
@check_rights("showUserLogs")
@login_required
def userLogs():
    cursor = db.connection().cursor(named_tuple=True)

    if current_user.is_admin():
        query = """SELECT CONCAT(users.last_name, ' ', users.first_name, ' ', users.patronymic) as bio,
                   COUNT(*) as count
                   FROM visit_logs
                   LEFT JOIN users on visit_logs.user_id = users.id
                   GROUP BY bio"""
        cursor.execute(query)
    else:
        query = """SELECT CONCAT(users.last_name, ' ', users.first_name, ' ', users.patronymic) as bio,
                   COUNT(*) as count
                   FROM visit_logs
                   LEFT JOIN users on visit_logs.user_id = users.id
                   WHERE users.login = %s
                   GROUP BY bio"""
        cursor.execute(query, (current_user.login,))

    logs = cursor.fetchall()
    logs.sort(key=lambda x: x[1], reverse=True)
    cursor.close()
    offset = (int(request.args.get("page", 1)) - 1) * PER_PAGE
    return render_template(
        "userLogs.html",
        logs=logs[offset : offset + PER_PAGE],
        lastPage=len(logs) // PER_PAGE + 1,
    )


@bp_logs.route("/saveToCSV")
@login_required
def saveToCSV():
    fields = []
    cursor = db.connection().cursor(named_tuple=True)

    match request.args.get("type"):
        case "visitLogs":
            if current_user.is_admin():
                query = """SELECT CONCAT(users.last_name, ' ', users.first_name, ' ', users.patronymic) as bio,
                           visit_logs.path as path,
                           visit_logs.created_at as created_at,
                           users.login as login
                           FROM visit_logs
                           LEFT JOIN users on visit_logs.user_id = users.id"""
                cursor.execute(query)
                fields = ["bio", "path", "created_at"]
            else:
                query = """SELECT CONCAT(users.last_name, ' ', users.first_name, ' ', users.patronymic) as bio,
                           visit_logs.path as path,
                           visit_logs.created_at as created_at,
                           users.login as login
                           FROM visit_logs
                           LEFT JOIN users on visit_logs.user_id = users.id
                           WHERE users.login = %s"""
                cursor.execute(query, (current_user.login,))
                fields = ["bio", "path", "created_at"]

        case "pageLogs":
            if current_user.is_admin():
                query = """SELECT visit_logs.path as path,
                           COUNT(*) as count
                           FROM visit_logs
                           LEFT JOIN users on visit_logs.user_id = users.id
                           GROUP BY path"""
                cursor.execute(query)
                fields = ["path", "count"]
            else:
                query = """SELECT visit_logs.path as path,
                           COUNT(*) as count
                           FROM visit_logs
                           LEFT JOIN users on visit_logs.user_id = users.id
                           WHERE users.login = %s
                           GROUP BY path"""
                cursor.execute(query, (current_user.login,))
                fields = ["path", "count"]

        case "userLogs":
            if current_user.is_admin():
                query = """SELECT CONCAT(users.last_name, ' ', users.first_name, ' ', users.patronymic) as bio,
                           COUNT(*) as count
                           FROM visit_logs
                           LEFT JOIN users on visit_logs.user_id = users.id
                           GROUP BY bio"""
                cursor.execute(query)
                fields = ["bio", "count"]
            else:
                query = """SELECT CONCAT(users.last_name, ' ', users.first_name, ' ', users.patronymic) as bio,
                           COUNT(*) as count
                           FROM visit_logs
                           LEFT JOIN users on visit_logs.user_id = users.id
                           WHERE users.login = %s
                           GROUP BY bio"""
                cursor.execute(query, (current_user.login,))
                fields = ["bio", "count"]

    logs = cursor.fetchall()

    match request.args.get("type"):
        case "visitLogs":
            logs.sort(key=lambda x: x[2], reverse=True)
        case "pageLogs":
            logs.sort(key=lambda x: x[1], reverse=True)
        case "userLogs":
            logs.sort(key=lambda x: x[1], reverse=True)

    match request.args.get("type"):
        case "visitLogs":
            logs = logs[
                (int(request.args.get("startPage")) - 1) * PER_PAGE
                + 1 :   # autoformatter:ignore
                int(request.args.get("endPage")) * PER_PAGE + 1
            ]
        case "pageLogs" | "userLogs":
            logs = logs[
                (int(request.args.get("startPage")) - 1)
                * PER_PAGE :   # autoformatter:ignore
                int(request.args.get("endPage")) * PER_PAGE
            ]

    csv_data = "№," + ",".join(fields) + "\n"
    for i, item in enumerate(logs):
        temp_csv_data = [str(getattr(item, field, "")) for field in fields]
        temp_csv_data.insert(
            0, str((int(request.args.get("startPage")) - 1) * PER_PAGE + i + 1)
        )
        csv_data += ",".join(temp_csv_data) + "\n"

    file = BytesIO()
    file.write(csv_data.encode("UTF-8"))
    file.seek(0)
    return send_file(file, download_name="logs.csv")
