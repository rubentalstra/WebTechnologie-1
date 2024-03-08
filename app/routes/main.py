from flask import Blueprint, render_template

from app.models.models import Film

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    films:list[Film] = Film.query.all()
    return render_template('index.html', films=films)