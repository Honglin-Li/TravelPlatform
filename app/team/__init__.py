from flask import Blueprint

team = Blueprint('team', __name__, template_folder='../templates/team', url_prefix='/team')

from . import views_team, views_activity