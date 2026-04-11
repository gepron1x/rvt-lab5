from flask import Blueprint, render_template
from ..extensions import db
from ..models import User

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    users = db.session.execute(db.select(User)).scalars().all()
    return render_template('index.html', users=users)