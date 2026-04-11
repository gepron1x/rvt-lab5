# run.py
from app import create_app
from app.extensions import db
from app.models import Role, User
from werkzeug.security import generate_password_hash

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        if not Role.query.first():
            admin_role = Role(name='Администратор')
            user_role = Role(name='Пользователь', description='Обычный пользователь')
            db.session.add_all([admin_role, user_role])
            db.session.commit()

            db.session.add(User(
                username='user',
                password_hash=generate_password_hash('qwerty'),
                first_name='Георгий',
                middle_name='Ярославович',
                last_name='Пронюк',
                role_id=admin_role.id
            ))
            db.session.commit()

    app.run(debug=True)