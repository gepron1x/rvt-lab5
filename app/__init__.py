from datetime import timedelta

from flask import Flask


from .extensions import db, login_manager
from .models import User, Role
def create_app():
    app = Flask(__name__)
    app.secret_key = 'goyslop'
    app.config['REMEMBER_COOKIE_DURATION'] = 31 * 24 * 3600  # 31 день
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from .routes.main import main_bp
    from .routes.auth import auth_bp
    from .routes.users import users_bp
    from .routes.visits import visits_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(visits_bp, prefix="/visits")

    from .routes.visits import log_visit # Before request for visit counts
    app.before_request(log_visit)

    return app