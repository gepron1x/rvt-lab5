# app/utils.py
from functools import wraps
from flask import flash, redirect, url_for, request, g
from flask_login import current_user
from .models import VisitLog, User


def has_role(required_role: str) -> bool:
    if not current_user.is_authenticated:
        return False
    role_name = current_user.role.name if current_user.role else None
    return required_role == role_name

def has_access(user: User) -> bool:
    if has_role("Администратор"):
        return True
    return current_user.id == user.id


def check_rights(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Для доступа необходимо войти в систему.", "warning")
                return redirect(url_for('auth.login'))

            if has_role(required_role):
                return f(*args, **kwargs)

            flash("У вас недостаточно прав для доступа к данной странице.", "danger")
            return redirect(url_for('main.index'))
        return decorated_function
    return decorator