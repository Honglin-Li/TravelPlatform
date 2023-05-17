"""
class & function list:
    load_user(user_id)
    User

"""
from ..extentions import db, login_manager, avatarUser, coverUser
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user, AnonymousUserMixin
from .team import Team
from flask import current_app
from .activity import JoinActivity
import re
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import random
from .tools import province

class Follow(db.Model):
    """
    follower关注了followed
    """
    __tablename__ = 'follows'

    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class AnonymousUser(AnonymousUserMixin):
    """
    匿名用户
    重写一些User里面不需要login_required的方法的默认返回值
    """
    def is_following(self):
        return False

    @property
    def is_leader(self):
        return False

    @property
    def is_admin(self):
        return False

    @property
    def id(self):
        return 0

login_manager.anonymous_user = AnonymousUser


class User(db.Model, UserMixin):
    """
    class structure:
        column:
            auth
            profile
            real info
            password
    """
    __tablename__ = 'users'

    def __repr__(self):
        return '<User %r>' % self.username

    #info:auth
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    last_seen = db.Column(db.DateTime)
    lock = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    #role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    #info:profile
    avatar = db.Column(db.String(128))
    cover = db.Column(db.String(128))
    gender = db.Column(db.String(8), default='不告诉你')
    birthday = db.Column(db.DateTime)
    about_me = db.Column(db.String(100))
    volunteer = db.Column(db.SmallInteger, default=0) #参与志愿者活动，即为志愿者，可以叠加多种志愿者

    #info:real identity
    name = db.Column(db.String(64))
    id_number = db.Column(db.String(18)) #TODO 删除
    phone = db.Column(db.String(15))
    address = db.Column(db.String(64))

    #常用出行人
    contacts = db.relationship('Contact', lazy='dynamic')
    #----------------信息脱敏---------------------
    @property
    def phone_show(self):
        reg = re.compile(r'(\d\d\d)(.*)(\d\d\d)')
        if self.phone:
            return reg.sub(r'\1*****\3' , self.phone)


    @property
    def id_number_show(self):
        reg = re.compile(r'(\d\d\d)(\d*)(\d\d\d)')
        if self.id_number:
            return reg.sub(r'\1*****\3', self.id_number)

    @property
    def is_leader(self):
        return self.leader_team is not None

    def is_team_leader(self, team_id):
        return Team.query.filter_by(id=team_id, leader_id=self.id).count()

    # password
    @property
    def password(self):
        raise AttributeError('password属性不可访问')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    #avatar & cover
    @property
    def avatar_url(self):
        filename = self.avatar if self.avatar else 'default-user.jpg'
        return avatarUser.url(filename)

    @property
    def cover_url(self):
        filename = self.cover if self.cover else 'default.jpg'
        return coverUser.url(filename)

    @staticmethod
    def get_username_by_id(user_id):
        return db.session.query(User.username).filter(User.id==user_id).scalar()

    @staticmethod
    def get_users(page=1):
        return User.query.order_by(User.timestamp.desc()).paginate(page, current_app.config['PAGECOUNT_USER'], False)

    #忘记密码----------------
    def generate_username_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'username': self.username})

    @staticmethod
    def get_username(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        return data.get('username')

    @staticmethod
    def get_rnd_password():
        seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+=-"
        rnd = ''.join(random.sample(seed, 5))
        return 'catyynet' + rnd

    #--------------关注----------------------
    #我关注的人
    followed = db.relationship('Follow', foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               cascade='all, delete-orphan', lazy='dynamic')
    #粉丝-关注我的人
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                cascade='all, delete-orphan', lazy='dynamic')

    #分页排序获取-我关注的人
    def follow_list(self, page=1):
        pagination = self.followed.order_by(Follow.timestamp.desc()).paginate(page, per_page=current_app.config[
            'PAGECOUNT_USER'], error_out=False)
        followed_list = [{'user': item.followed, 'timestamp': item.timestamp} for item in pagination.items]
        return pagination, followed_list

    #分页排序获取-关注我的人
    def fans_list(self, page=1):
        pagination = self.followers.order_by(Follow.timestamp.desc()).paginate(page, per_page=current_app.config[
            'PAGECOUNT_USER'], error_out=False)
        follower_list = [{'user': item.follower, 'timestamp': item.timestamp} for item in pagination.items]
        return pagination, follower_list

    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is not None

    def follow(self, user):
        if not self.is_following(user):
            follow = Follow(follower=self, followed=user)
            db.session.add(follow)
            db.session.commit()

    def unfollow(self, user):
        follow = self.followed.filter_by(followed_id=user.id).first()
        if follow:
            db.session.delete(follow)
            db.session.commit()

    @property
    def follower_count(self):
        return self.followers.count()

    @property
    def followed_count(self):
        return self.followed.count()

    #各种relationship------------团队---------------------------------
    leader_team = db.relationship('Team', backref='leader',foreign_keys=[Team.leader_id], uselist=False)
    user_teams = db.relationship('TeamUser', backref=db.backref('user', lazy='joined'),
                                 lazy = 'dynamic', cascade='all, delete-orphan')
    @property
    def teams_joined(self):
        return [item.team for item in self.user_teams.order_by('team_users.timestamp desc').all()]

    @property
    def joined_team_count(self):
        return self.user_teams.count()

    #辅助工具
    @staticmethod
    def get_user(id):
        if id == 0:
            return current_user
        else:
            return User.query.get_or_404(id)

    #---------------relationship-----------活动
    activities_followed = db.relationship('FollowActivity', backref=db.backref('user', lazy='joined'),
                                          lazy='dynamic', cascade='all, delete-orphan')
    joins_activity = db.relationship('JoinActivity', lazy='dynamic', backref=db.backref('user', lazy='joined'))

    questions_activity = db.relationship('ActivityQuestion', lazy='dynamic', backref=db.backref('user', lazy='joined'))

    supports = db.relationship('CrowdFunding', lazy='dynamic', backref=db.backref('user', lazy='joined'))

    #TODO 分页
    def activities_follow(self):
        return [follow.activity for follow in self.activities_followed.order_by('follow_activities.timestamp desc').all()]

    def activities_join(self):
        return [join.activity for join in self.joins_activity.order_by(JoinActivity.timestamp.desc()).all()]

    def activities_join_unpay(self):
        return [join.activity for join in self.joins_activity.filter(JoinActivity.state==False).order_by(JoinActivity.timestamp.desc()).all()]

    @property
    def activity_join_count(self):
        return self.joins_activity.count()

    @property
    def activity_follow_count(self):
        return self.activities_followed.count()

    @property
    def activity_join_unpay_count(self):
        return self.joins_activity.filter(JoinActivity.state==False).count()


class Contact(db.Model):
    __tablename__ = 'contacts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(10), nullable=False)
    identity = db.Column(db.String(18), nullable=False)
    phone = db.Column(db.String(15))
    gender = db.Column(db.SmallInteger)  # 性别：0-男-1-女
    age = db.Column(db.SmallInteger)
    province = db.Column(db.SmallInteger, default=0)  # province_list 的 index, 默认0-河南省

    @property
    def phone_show(self):
        reg = re.compile(r'(\d\d\d)(.*)(\d\d\d)')
        return reg.sub(r'\1*****\3', self.phone)

    @property
    def identity_show(self):
        reg = re.compile(r'(\d\d\d)(\d*)(\d\d\d)')
        return reg.sub(r'\1*****\3', self.identity)

    @property
    def province_show(self):
        return province[self.province]













