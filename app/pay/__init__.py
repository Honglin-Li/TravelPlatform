from flask import Blueprint

pay = Blueprint('pay', __name__, template_folder='../templates/pay', url_prefix='/callback')
from . import views_alipay
