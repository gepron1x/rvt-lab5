from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash

from ..extensions import db
from ..models import User, Role
from ..rights import check_rights, has_access, has_role
from ..validations import validate_user_data
users_bp = Blueprint('users', __name__)

@users_bp.route('/user/<int:user_id>')
def view_user(user_id):
    user = db.get_or_404(User, user_id)
    return render_template('view_user.html', user=user)

@users_bp.route('/user/create', methods=['GET', 'POST'])
@check_rights("Администратор")
def create_user():
    roles = db.session.execute(db.select(Role)).scalars().all()
    errors = {}
    if request.method == 'POST':
        errors = validate_user_data(request.form)
        if not errors:
            try:
                new_user = User(
                    username=request.form['username'],
                    password_hash=generate_password_hash(request.form['password']),
                    first_name=request.form['first_name'],
                    last_name=request.form['last_name'],
                    middle_name=request.form['middle_name'],
                    role_id=request.form.get('role_id') or None
                )
                db.session.add(new_user)
                db.session.commit()
                flash("Пользователь успешно создан!", "success")
                return redirect(url_for('main.index'))
            except Exception as e:
                db.session.rollback()
                flash(f"Ошибка при сохранении в базу данных: {str(e)}", "danger")

    return render_template('create_user.html', roles=roles, errors=errors)

@users_bp.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_user(user_id: int):
    user = db.get_or_404(User, user_id)
    if not has_access(user):
        flash("У вас недостаточно прав для доступа к данной странице.", "danger")
        return redirect(url_for('main.index'))

    roles = db.session.execute(db.select(Role)).scalars().all()
    errors = {}
    if request.method == 'POST':
        errors = validate_user_data(request.form, is_edit=True)
        if not errors:
            try:
                user.first_name = request.form.get('first_name')
                user.last_name = request.form.get('last_name')
                user.middle_name = request.form.get('middle_name')

                role_id = request.form.get('role_id')
                user.role_id = int(role_id) if role_id else None

                db.session.commit()
                flash(f"Данные пользователя {user.username} успешно обновлены!", "success")
                return redirect(url_for('main.index'))

            except Exception as e:
                db.session.rollback()
                flash(f"Ошибка при сохранении в базу данных: {str(e)}", "danger")
            db.session.commit()
            flash("Пользователь успешно редактирован!", "success")
            return redirect(url_for('main.index'))
    return render_template('edit_user.html', user=user, roles=roles, errors=errors,
                           is_admin=has_role("Администратор"))


@users_bp.route('/user/<int:user_id>/delete', methods=['POST'])
@check_rights("Администратор")
def delete_user(user_id):
    user = db.get_or_404(User, user_id)
    if user.id == current_user.id:
        flash("Вы не можете удалить самого себя!", "danger")
        return redirect(url_for('main.index'))

    try:
        db.session.delete(user)
        db.session.commit()
        flash(f"Пользователь {user.full_name} удален.", "success")
    except Exception as e:
        db.session.rollback()
        flash("Ошибка при удалении пользователя.", "danger")
    return redirect(url_for('main.index'))