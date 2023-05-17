from flask import Blueprint

admin = Blueprint('admin', __name__, url_prefix='/admin', template_folder='../templates/admin')

from . import views, views_team, views_outdoor