from flask import Blueprint, redirect, url_for, request, flash, render_template
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from ..extensions import db
from ..models import User
from ..validations import validate_password

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        user = db.session.execute(
            db.select(User).filter_by(username=username)
        ).scalars().first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=remember)
            flash('Вы успешно вошли в систему!', 'success')

            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        else:
            flash('Неверный логин или пароль', 'danger')

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из аккаунта', 'info')
    return redirect(url_for('main.index'))

def validate_change_password_form(data):
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')
    repeat_new_password = data.get('repeat_new_password', '')
    errors = {}
    if not check_password_hash(current_user.password_hash, old_password):
        errors['old_password'] = 'Неверный пароль'
    if not validate_password(new_password):
        errors['new_password'] = 'Пароль не соответствует требованиям безопасности'
    if new_password != repeat_new_password:
        errors['repeat_new_password'] = 'Пароли не совпадают'
    return errors


@auth_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        errors = validate_change_password_form(request.form)
        if errors:
            print(errors)
            return render_template('change_password.html', errors=errors)
        new_password = request.form.get('new_password', '')

        current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()

        flash('Пароль успешно изменён!', 'success')
        return redirect(url_for('main.index'))


    return render_template("change_password.html", errors={})