from flask import Blueprint

user = Blueprint('user', __name__, template_folder='../templates/user', url_prefix='/user')
from . import view_profile
