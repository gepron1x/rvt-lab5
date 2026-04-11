import csv
from io import StringIO

from flask import request, Blueprint, render_template, abort, make_response
from flask_login import current_user
from sqlalchemy import text, func, desc

from ..models import VisitLog, User
from ..extensions import db
from ..rights import has_role, check_rights

visits_bp = Blueprint('visits', __name__)

PAGE_SIZE = 10

def log_visit():
    if request.endpoint and not request.path.startswith('/static'):
        user_id = current_user.id if current_user.is_authenticated else None
        log = VisitLog(
            path=request.path,
            user_id=user_id
        )
        db.session.add(log)
        db.session.commit()

@visits_bp.route('/visits')
def visits():
    page = request.args.get('page', 1, type=int)
    stmt = db.select(VisitLog).order_by(VisitLog.created_at.desc())
    if not has_role("Администратор"):
        stmt = stmt.filter_by(user_id=current_user.id)
    pagination = db.paginate(stmt, page=page, per_page=PAGE_SIZE)
    return render_template("visits/visits.html",
                           logs=pagination.items,
                           pagination=pagination,
                           page=page, is_admin=has_role("Администратор"))

def make_pages_report():
    stmt = db.select(
        VisitLog.path,
        func.count().label('visit_count')
    ).group_by(VisitLog.path).order_by(desc('visit_count'))

    results = db.session.execute(stmt).fetchall()
    table = [['№', 'Страница', 'Количество посещений']]
    for idx, (path, count) in enumerate(results, 1):
        table.append([idx, path, count])
    return table

def make_users_report():
    stmt = db.select(
        User,  # The whole User object
        func.count().label('visit_count')
    ).outerjoin(
        VisitLog, User.id == VisitLog.user_id
    ).group_by(
        User.id
    ).order_by(
        desc('visit_count')
    )
    results = db.session.execute(stmt).fetchall()
    table = [['№', 'Пользователь', 'Количество посещений']]
    for idx, (user, count) in enumerate(results, 1):
        table.append([idx, user.full_name if user else 'Неаутентифицированный пользователь', count])
    return table

@visits_bp.route('/report/pages')
@check_rights("Администратор")
def report_pages():
    table = make_pages_report()
    return render_template("visits/report.html",
                           header=table[0],
                           rows=table[1:],
                           report_title="Отчёт по страницам", report_type='pages')

@visits_bp.route('/report/users')
@check_rights("Администратор")
def report_users():
    table = make_users_report()
    return render_template("visits/report.html",
                           header=table[0],
                           rows=table[1:],
                           report_title="Отчёт по пользователям", report_type='users')

@visits_bp.route('/report/<report_type>/csv')
@check_rights("Администратор")
def export_csv(report_type: str):
    if report_type == 'pages':
        table = make_pages_report()
    elif report_type == 'users':
        table = make_users_report()
    else:
        abort(404)
    si = StringIO()
    cw = csv.writer(si, delimiter=';')
    for row in table:
        cw.writerow(row)

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=report_pages.csv"
    output.headers["Content-type"] = "text/csv; charset=utf-8"
    return output




