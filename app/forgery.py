from forgery_py import (
    address,
    basic,
    lorem_ipsum,
    name,
    date
)
from forgery_py.forgery import internet
from .models.team import Team
from .models.outdoorType import OutdoorType
from .models.user import User
from .extentions import db
from random import seed, randint, sample
from sqlalchemy.exc import IntegrityError
from flask import flash


def move_contact():
    from .models.activity import ActivityContact, JoinActivity
    from .models.user import Contact
    ac_list = ActivityContact.query.all()
    for ac in ac_list:
        #创建联系人
        if ac.join_id:  #不知道为什么，存在join_id为空的
            join = JoinActivity.query.get_or_404(ac.join_id)
            user_id = join.user_id
            contact = Contact(
                user_id=user_id,
                name = ac.name,
                identity = ac.identity,
                phone = ac.phone,
                gender = ac.gender,
                age = ac.age,
            )
            db.session.add(contact)
            db.session.commit()
            #更新原始联系人信息
            ac.contact_id = contact.id
            db.session.add(ac)
            db.session.commit()


def clear_test_user():
    users = User.query.all()
    for user in users:
        if user.verify_password('123'):
            db.session.delete(user)
        db.session.commit()


def show_test_user():
    users = User.query.all()
    for user in users:
        if user.verify_password('123'):
            from flask import flash
            flash(user.username)


def add_club():
    from .models.activity import volunteer_type
    for item in volunteer_type:
        #创建用户
        user = User.query.filter_by(username=volunteer_type[item]).first()
        if user:
            continue
        user = User()
        user.username = volunteer_type[item]
        user.password = 'lihonglin92999'
        db.session.add(user)
        db.session.commit()
        #创建团队
        team = Team.query.filter_by(name=volunteer_type[item]).first()
        if not team:
            team = Team()
            team.name = volunteer_type[item]
            team.leader_id = user.id
            team.created_by = user.id
            team.classify = 1
            team.approved = True
            db.session.add(team)
            db.session.commit()
            #加入队长
            team.join(user, is_admin=True)


def gene_users(count=100):
    from random import seed, randint
    from sqlalchemy.exc import IntegrityError

    gender = ('男', '女', '不告诉你')
    seed()
    for i in range(count):
        fake_user = User()
        fake_user.username = internet.user_name(True)
        fake_user.email = fake_user.username + '@test.com'
        fake_user.password = '123'
        fake_user.name = name.full_name()
        fake_user.about_me = lorem_ipsum.sentence()[0:99]
        fake_user.timestamp = date.date(past=True)
        fake_user.birthday = date.date(past=True)
        fake_user.gender = gender[randint(0,2)]
        fake_user.phone = address.phone()
        fake_user.address = address.street_address()
        fake_user.id_number = ''.join([str(randint(0,9)) for i in range(18)])
        db.session.add(fake_user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def gene_teams(count=100):
    from random import seed, randint, sample
    from sqlalchemy.exc import IntegrityError

    seed()
    user_count = User.query.count()
    types = OutdoorType.show_list()
    for i in range(count):
        fake_team = Team()
        fake_team.name = name.company_name() + '的户外团队'
        leader = User.query.offset(randint(0, count-1)).first()
        fake_team.created_by = leader.id
        fake_team.leader_id = leader.id
        fake_team.description = lorem_ipsum.sentence()[:99]
        fake_team.timestamp = date.date(past=True)
        fake_team.types = sample(types, randint(1,7))
        db.session.add(fake_team)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def gene_members(member_count=50):
    seed()
    teams = Team.query.all()
    users = User.query.all()
    for team in teams:
        for user in sample(users, randint(5, member_count)):
            if not team.is_member(user):
                team.join(user)
    db.session.commit()


def fake_follow():
    seed()
    users = User.query.all()
    follow = User.query.all()
    for user in users:
        for f in sample(follow, 2):
            print(f.username)
            user.follow(f)


def test_outdoor():
    admin = User.query.filter_by(username='admin').first()
    types = [['南太行', 100, 'outdoor_type/nantaihang.gif'],
             ['户外登山', 90, 'outdoor_type/huwaidengshan.jpg'],
             ['攀岩', 80, 'outdoor_type/panyan.jpg'],
             ['骑行', 70, 'outdoor_type/qixing.jpg'],
             ['健步走',60, 'outdoor_type/jianbuzou.jpg'],
             ['垂钓', 50, 'outdoor_type/chuidiao.jpg'],
             ['漂流', 40, 'outdoor_type/piaoliu.jpg'],
             ['跑步', 30, 'outdoor_type/paobu.jpg']
             ]
    for t in types:
        outdoor_type = OutdoorType()
        outdoor_type.name = t[0]
        outdoor_type.weight = t[1]
        outdoor_type.image = t[2]
        outdoor_type.created_by = admin.id
        db.session.add(outdoor_type)
        db.session.commit()








