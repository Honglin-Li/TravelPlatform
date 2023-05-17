from flask import Flask, url_for, render_template, current_app
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_uploads import UploadSet, IMAGES
from flask_ckeditor import CKEditor
from flask_nav import Nav
from flask_nav.elements import Navbar, View, Separator, Subgroup, Link
from flask_mail import Mail, Message
from threading import Thread
from alipay import AliPay
import os


bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
ckeditor = CKEditor()
mail = Mail()


nav = Nav()


@nav.navigation()
def top_nav():
    return Navbar('小猫游园',
                  View('主页', 'index'),
                  View('活动', 'team.activities_search_home'),
                  View('团队', 'team.teams_search_home'),
                  View('申请俱乐部', 'team.create_team'),
                  View('我的主页', 'user.profile_me'),
                  View('我的俱乐部', 'team.team_me'),
                  View('致赞助商的一封信', 'invest')
                  )


#头像上传
avatarUser = UploadSet('avatarUser', IMAGES)
avatarTeam = UploadSet('avatarTeam', IMAGES)
coverUser = UploadSet('coverUser', IMAGES)
imgTeam = UploadSet('imgTeam', IMAGES)
coverPost = UploadSet('coverPost', IMAGES)
commonImage = UploadSet('commonImage', IMAGES)

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
login_manager.login_message = '您需要登陆访问该资源哦'


def send_msg(to, title, template, **kwargs):
    from manage import app
    msg = Message(title, sender='小猫游园<catyynet@163.com>', recipients=to)
    msg.body = render_template(template+'.txt', **kwargs)
    msg.html = render_template(template+'.html', **kwargs)
    thr = Thread(target=send_sync_msg, args=[app, msg])
    thr.start()
    return thr


def send_sync_msg(app, msg):
    with app.app_context():
        mail.send(msg)

if os.getenv('FLASK_CONFIG') == 'production':
    alipay = AliPay(
        appid='2018080360933015',
        app_notify_url=None,  # 默认回调url
        sign_type="RSA2",
        alipay_public_key_path=r'/home/deploy/alipay_public_key',
        app_private_key_path=r'/home/deploy/app_secret_key',
        debug=False
    )
else:
    alipay = AliPay(
        appid='2016091800540443',
        app_notify_url=None,  # 默认回调url
        sign_type="RSA2",
        alipay_public_key_path=os.path.join(os.getcwd(), 'app', 'key', 'alipay_public_key'),
        app_private_key_path=os.path.join(os.getcwd(), 'app', 'key', 'app_secret_key'),
        debug=True
    )
