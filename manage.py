import os
"""import pymysql
pymysql.install_as_MySQLdb()"""

from app import create_app
from flask_script import Manager, Shell, Command
from flask_migrate import Migrate, MigrateCommand
from app.extentions import db
from app.models.user import User
from app.models.outdoorType import OutdoorType
from app.models.team import Team, TeamUser
from app.models.activity import Activity
import logging

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    filemode='a',)
logger = logging.getLogger('')


@manager.shell
def make_shell_context():
    return dict(app=app, db=db, User=User, Team=Team, OutdoorType=OutdoorType, TeamUser=TeamUser, Activity=Activity)
manager.add_command('db', MigrateCommand)


@manager.command
def createdb():
    db.create_all()
    #create admin
    admin = User()
    admin.username = 'admin'
    admin.email = 'lucky_lark@163.com'
    admin.password = '123456'
    admin.is_admin = True
    db.session.add(admin)
    db.session.commit()


@manager.command
def create_outdoor():
    admin = User.query.filter_by(username='admin').first()
    #添加户外分类
    types = [['南太行', 100, 'outdoor_type/nantaihang.gif'],
             ['登山', 90, 'outdoor_type/dengshan.jpg'],
             ['重装', 80, 'outdoor_type/zhongzhuang.jpg'],
             ['露营', 70, 'outdoor_type/luying.jpg'],
             ['骑行', 60, 'outdoor_type/qixing.jpg'],
             ['摄影', 50, 'outdoor_type/sheying.jpg'],
             ['休闲', 40, 'outdoor_type/xiuxian.jpg'],
             ['景区', 30, 'outdoor_type/jingqu.jpg'],
             ['自驾', 30, 'outdoor_type/zijia.jpg'],
             ['其他', 30, 'outdoor_type/qita.jpg']
             ]
    for t in types:
        outdoor_type = OutdoorType()
        outdoor_type.name = t[0]
        outdoor_type.weight = t[1]
        outdoor_type.image = t[2]
        outdoor_type.created_by = admin.id
        db.session.add(outdoor_type)
        db.session.commit

if __name__ == '__main__':
    manager.run()
