"""
CLASS Activity

"""
from ..extentions import db
from datetime import datetime, timedelta
from .outdoorType import activity_types, OutdoorType
from ..extentions import coverPost
from flask_login import current_user
from sqlalchemy.sql.expression import and_, or_
from sqlalchemy.sql import func
from flask import current_app, flash, session, url_for
import re
from ..tools.photo import qrcode_url_string, qrcode_cover, qrcode_img



"""
报名方式&志愿者类型
"""


#报名类
class RegistrationWay:
    PERSION = 0x01   #个人报名
    TEAM = 0x02      #团队报名
    VOLUNTEER = 0x04 #志愿者报名

#界面显示用
registration_way = {
    RegistrationWay.PERSION: '个人报名',
    RegistrationWay.TEAM: '团队报名',
    RegistrationWay.VOLUNTEER:  '志愿者报名'
}


class Volunteer:
    Server = 0x01
    Photographer = 0x02
    Orienteering = 0x04
    Judge = 0x08
    Leader = 0x10
    Guide = 0x20
    Entertainment = 0x40

volunteer_type = {
    Volunteer.Server: '服务志愿者',
    Volunteer.Photographer : '摄影志愿者',
    Volunteer.Orienteering : '定向越野志愿者',
    Volunteer.Judge : '徒步裁判志愿者',
    Volunteer.Leader : '户外领队志愿者',
    Volunteer.Guide : '导游志愿者',
    Volunteer.Entertainment : '文娱志愿者'
  }

"""
活动类
"""


class Activity(db.Model):
    """
    id
    标题/创建时间/归属团队/封面/
    开始日期/结束日期/天数
    集合地点/目的地
    联系电话
    最多参与人数/活动实际参与人数
    价钱/儿童价
    强度指数/风景指数
    行程安排
    浏览次数
    """
    __tablename__ = 'activities'

    def __repr__(self):
        return '<Activity : %r>' % self.name

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, index=True, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    belong_to_team = db.Column(db.Integer, db.ForeignKey('teams.id'))
    cover = db.Column(db.String(128))
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    days = db.Column(db.SmallInteger)
    rally_site = db.Column(db.String(20))
    destination = db.Column(db.String(20))
    phone = db.Column(db.String(15))
    maximum = db.Column(db.SmallInteger)
    members = db.Column(db.SmallInteger, default=0)
    price = db.Column(db.SmallInteger, nullable=False)
    child_price = db.Column(db.SmallInteger)
    intensity_index = db.Column(db.SmallInteger, nullable=False)
    landscape_index = db.Column(db.SmallInteger, nullable=False)
    introduce = db.Column(db.Text, nullable=False)
    view_count = db.Column(db.Integer, default=0)
    registration = db.Column(db.SmallInteger, default=1) #默认仅接受个人报名
    qrcode = db.Column(db.String(128)) #二维码
    team_join_info = db.Column(db.Text)
    #admin-property
    top = db.Column(db.Boolean, default=False) #全站置顶
    top_team = db.Column(db.Boolean, default=False) #团内内置顶

    @property
    def qrcode_url(self):
        if not self.qrcode:
            if self.cover:
                img = qrcode_cover(url_for('team.activity', id=self.id, _external=True), coverPost.path(self.cover))
            else:
                img = qrcode_cover(url_for('team.activity', id=self.id, _external=True), coverPost.path('default.jpg'))
            self.qrcode = img
            db.session.add(self)
        return qrcode_url_string(self.qrcode)

    # 重新生成二维码
    def gene_qrcode(self):
        if self.cover:
            img = qrcode_cover(url_for('team.activity', id=self.id, _external=True), coverPost.path(self.cover))
        else:
            img = qrcode_cover(url_for('team.activity', id=self.id, _external=True), coverPost.path('default.jpg'))
        return img

    # --------------------------活动类型---------------------------
    types = db.relationship('OutdoorType', secondary=activity_types, backref=db.backref('activities', lazy='dynamic'))
    teams_joind = db.relationship("TeamJoinActivity", lazy='dynamic', backref=db.backref('activity', lazy='joined'))

    def view(self):
        if session.get('activity_viewcount'):
            return
        session['activity_viewcount'] = True
        self.view_count += 1
        db.session.add(self)

    solutions = db.relationship('ActivitySolution',
                                lazy='dynamic',
                                backref=db.backref('activity', lazy='joined'),
                                )
    @property
    def solotion_count(self):
        return self.solutions.count()

    @property
    def cover_url(self):
        filename = self.cover or 'default.jpg'
        return coverPost.url(filename)

    @property
    def past(self):
        return datetime.now() > (self.start_date + timedelta(days=1))  # 当天都还可以报名

    def register(self, way):
        return self.registration & way

    #满员-未填写maximuam为不限人数
    @property
    def full(self):
        if self.maximum:
            return self.paid_member_count >= self.maximum
        return False

    # ------------------获取各种活动集合--------------------------

    @staticmethod
    def get_activities_home_panel():
        outdoor = OutdoorType.query.filter_by(name='南太行').first()
        return outdoor.activities.order_by(Activity.timestamp.desc()).limit(4).all()

    @staticmethod
    def get_activities_home():
        # TODO 过期的不要
        return Activity.query.filter_by(top=True).order_by(Activity.timestamp.desc()).limit(5).all()

    @staticmethod
    def get_activities_search(keyword, outdoor, days, sort, page=1):
        activities = Activity.query
        if outdoor != 'None': #户外类型
            t = OutdoorType.query.get(int(outdoor))
            activities = t.activities
        if keyword:#允许多个空格分隔的搜索关键字
            keywords = keyword.split()
            for k in keywords:
                activities = activities.filter(Activity.name.like('%'+k+'%'))
        if days != 'None': #出行天数
            if days == '1':
                activities = activities.filter(Activity.days == 1)
            elif days == '3':
                activities = activities.filter(or_(Activity.days == 2, Activity.days == 3))
            elif days == '7':
                activities = activities.filter(and_(Activity.days > 3, Activity.days < 8))
            elif days == '15':
                activities = activities.filter(and_(Activity.days > 7, Activity.days < 16))
            else:
                activities = activities.filter(Activity.days > 15)
        if sort != 'None':#排序
            if sort == '1':
                activities = activities.order_by(Activity.view_count.desc())
            elif sort == '2':
                activities = activities.order_by(Activity.price.asc())
            elif sort == '3':
                activities = activities.order_by(Activity.price.desc())
            else:
                activities = activities.order_by(Activity.timestamp.desc())
        else:
            activities = activities.order_by(Activity.timestamp.desc())
        return activities.paginate(page, current_app.config['PAGECOUNT_ACTIVITY'], error_out=False)


    @staticmethod
    def get_activities(page=1):
        pagination = Activity.query.order_by(Activity.timestamp.desc()).paginate(page,
                        current_app.config['PAGECOUNT_ACTIVITY'], error_out=False)
        return pagination

    # -----------------关注收藏-----------------
    followers = db.relationship('FollowActivity', lazy='dynamic', backref=db.backref('activity', lazy='joined'),
                                cascade='all, delete-orphan')

    @property
    def follow_count(self):
        return self.followers.count()

    #TODO 分页排序
    @property
    def follow_members(self):
        return [follow.user for follow in self.followers.order_by(FollowActivity.timestamp.desc()).all()]

    def is_following(self, user):
        return user.is_authenticated and (self.followers.filter_by(user_id=user.id).first() is not None)

    def follow(self, user):
        if not self.is_following(user):
            follow = FollowActivity(user_id=user.id, activity_id=self.id)
            db.session.add(follow)

    def unfollow(self, user):
        follow = self.followers.filter_by(user_id=user.id).first()
        if follow:
            db.session.delete(follow)

    #---------------报名----------
    joins = db.relationship('JoinActivity', lazy='dynamic', backref=db.backref('activity', lazy='joined'))

    @property
    def paid_member_count(self):
        count = db.session.query(func.sum(JoinActivity.count)).filter_by(activity_id=self.id, state=True).scalar()
        return count if count else 0

    @property
    def member_count(self):
        count = db.session.query(func.sum(JoinActivity.count)).filter_by(activity_id=self.id).scalar()
        return count if count else 0

    def joined(self, user):
        if user.is_anonymous:
            return False
        return self.joins.filter_by(user_id=user.id).count()

    def paid(self, user):
        if user.is_anonymous:
            return False
        return JoinActivity.query.filter(JoinActivity.state==True, JoinActivity.user_id==user.id,
                                         JoinActivity.activity_id==self.id).count()

    @property
    def unpaid_id(self, user=current_user):
        return self.joins.filter_by(user_id=user.id, state=False).first().id

    #TODO 分页
    @property
    def users_joined(self):
        return [join.user for join in self.joins.all()] #仅筛选付费用户

    # TODO 分页
    @property
    def users_joined_paid(self):
        return [join.user for join in self.joins.filter_by(state=1).all()]  # 仅筛选付费用户

    # 个人报名
    def sign_up(self,child_count, contacts, sln, comment, team_id, volunteer):
        from .team import TeamJoinActivity, Team
        count = len(contacts) if isinstance(contacts, list) else 1  # 报名人数-志愿者
        price = TeamJoinActivity.get_price(team_id, self.id) if team_id else self.price  #报名价钱-团队报名
        child_price = TeamJoinActivity.get_child_price(team_id, self.id) if team_id else self.child_price  #报名价钱-团队报名
        child_price = child_price if child_price else price
        # 创建报名信息
        join_info = JoinActivity()
        #报名的三种方式
        if team_id:
            join_info.registration = RegistrationWay.TEAM
            join_info.team_id = team_id
        elif volunteer:
            join_info.registration = RegistrationWay.VOLUNTEER
            join_info.volunteer = volunteer
        else:
            join_info.registration = RegistrationWay.PERSION
        join_info.price = child_count * child_price + (count-child_count)*price
        join_info.child_count = child_count
        join_info.user_id = current_user.id
        join_info.activity_id = self.id
        join_info.count = count
        join_info.comment = comment
        join_info.state = False
        join_info.solution = sln if sln else None
        join_info.trade_no = datetime.now().strftime('%Y%m%d%H%M%S') + str(current_user.id)
        db.session.add(join_info)
        db.session.commit()
        # --创建出行人信息--这里仅接收contactID
        if volunteer:
            db.session.add(ActivityContact(
                join_id=join_info.id,
                contact_id=contacts
            ))
        else:
            for contact in contacts:
                db.session.add(ActivityContact(
                    join_id=join_info.id,
                    contact_id=contact))
        # 加入活动所在团队
        join_info.activity.team.join(current_user)
        #志愿者-更新志愿者类型+加入志愿者团队
        if volunteer:
            if not current_user.volunteer:
                current_user.volunteer = 0
            current_user.volunteer = current_user.volunteer | join_info.volunteer
            db.session.add(current_user)
            team = Team.query.filter_by(name=volunteer_type[join_info.volunteer]).first()
            team.join(current_user)
        db.session.commit()
        return join_info

    # 编辑
    def join_edit(self,child_count, contacts, sln, comment, join_info):
        from .team import TeamJoinActivity, Team
        count = len(contacts) if isinstance(contacts, list) else 1  # 报名人数-志愿者
        price = TeamJoinActivity.get_price(join_info.team_id, self.id) if join_info.team_id else self.price  # 报名价钱-团队报名
        child_price = TeamJoinActivity.get_child_price(join_info.team_id, self.id) if join_info.team_id else self.child_price  # 报名价钱-团队报名
        child_price = child_price if child_price else price  # 没有儿童价格，但是给儿童报名的
        join_info.price = price * (count-child_count) + child_count*child_price
        join_info.count = count
        #修改报名信息
        join_info.solution = sln if sln else None
        join_info.comment = comment
        join_info.child_count = child_count
        join_info.contacts = []
        # --修改出行人信息--
        if join_info.registration == RegistrationWay.VOLUNTEER:
            join_info.contacts.append(ActivityContact(
                join_id=join_info.id,
                contact_id=contacts
            ))
        else:
            for contact in contacts:
                join_info.contacts.append(ActivityContact(
                    join_id=join_info.id,
                    contact_id=contact))
        db.session.add(join_info)
        db.session.commit()
        return join_info

    # 团队报名-不带个人信息，不加入JoinActivity表
    def join_team(self, team_id, phone, sln, price, child_price, team_content):
        from .team import TeamJoinActivity
        join = TeamJoinActivity(activity_id=self.id,
                                team_id = team_id,
                                team_content= team_content,
                                team_price = max(price, self.price),
                                child_price = max(child_price, self.child_price),
                                phone = phone,
                                solution = sln)
        db.session.add(join)
        db.session.commit()
        # 生成二维码
        if self.cover:
            qrcode = qrcode_cover(url_for('team.activity_index_team', id=join.id, _external=True),
                                  coverPost.path(self.cover))
        else:
            qrcode = qrcode_cover(url_for('team.activity_index_team', id=join.id, _external=True),
                                  coverPost.path('default.jpg'))
        join.qrcode = qrcode
        db.session.add(join)
        return join

    def get_team_content(self, team_id):
        from .team import TeamJoinActivity
        l = db.session.query(TeamJoinActivity.team_content
                         ).filter(TeamJoinActivity.team_id==team_id,TeamJoinActivity.activity_id==self.id).scalar()
        return l[0]

    # 获取所有报名信息
    # TODO 分页----这个分页比较难做
    @staticmethod
    def get_registration_details(activity_id, team_id=0):
        from .user import User
        from .team import Team
        from .user import Contact
        result = db.session.query(JoinActivity, ActivityContact, Contact).select_from(JoinActivity).filter(
            JoinActivity.activity_id == activity_id).join(ActivityContact, JoinActivity.id == ActivityContact.join_id).join(
            Contact, ActivityContact.contact_id == Contact.id
        )
        if team_id:
            result = result.filter(JoinActivity.team_id==team_id)
        result = result.all()
        details = []
        for item in result:
            info = {
                'serial_number' : item.ActivityContact.id,
                'timestamp': item.JoinActivity.timestamp,
                'user_id' : item.JoinActivity.user_id,
                'username' : User.get_username_by_id(item.JoinActivity.user_id),
                'state' : item.JoinActivity.state,
                'province': item.Contact.province,
                'solution_id' : item.JoinActivity.solution,
                'solution' : ActivitySolution.get_sln_name_by_id(item.JoinActivity.solution),
                'volunteer': item.JoinActivity.volunteer,
                'volunteer_name': item.JoinActivity.volunteer_name,
                'team_id' : item.JoinActivity.team_id,
                'team_name': Team.get_team_name_by_id(item.JoinActivity.team_id),
                'name' : item.Contact.name,
                'identity': item.Contact.identity,
                'age': item.Contact.age,
                'gender': item.Contact.gender,
                'phone': item.Contact.phone,
                'registration': item.JoinActivity.registration_way
            }
            details.append(info)
        return details

    # ------------------咨询-----------------
    counsel = db.relationship('ActivityQuestion', lazy='dynamic', backref=db.backref('activity', lazy='joined'))

    @property
    def counsel_reverse(self):
        return self.counsel.order_by('activity_questions.timestamp desc').all()
    # TODO  分页


class ActivitySolution(db.Model):
    __tablename__ = 'activity_solutions'

    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))
    name = db.Column(db.String(20), nullable=False)
    detail = db.Column(db.String(500), nullable=False)

    @staticmethod
    def add_solution(activity, name, detail):
        sln = ActivitySolution(activity_id=activity.id,
                               name=name,
                               detail=detail)
        db.session.add(sln)

    @staticmethod
    def add_solution_list(activity, solutions):
        for sln in solutions:
            ActivitySolution.add_solution(activity, sln['name'], sln['detail'])

    def edit(self, name, detail):
        self.name=name
        self.detail=detail
        db.session.add(self)

    @staticmethod
    def delete(id):
        sln = ActivitySolution.query.get_or_404(id)
        db.session.delete(sln)

    @staticmethod
    def get_sln_name_by_id(sln_id):
        return db.session.query(ActivitySolution.name).filter(ActivitySolution.id==sln_id).scalar()


class JoinActivity(db.Model):
    __tablename__ = 'join_activities'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    count = db.Column(db.Integer, nullable=False) #订单几人
    child_count = db.Column(db.SmallInteger)  # 其中儿童人数
    price = db.Column(db.Integer) #订单总价钱
    state = db.Column(db.Boolean, default=False) #0-未付款 1-已付款
    trade_no = db.Column(db.String(40)) # 订单账号
    alipay_no = db.Column(db.String(40)) # 支付宝返回流水号
    registration = db.Column(db.SmallInteger) #报名的三种类型
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id')) #团队报名
    solution = db.Column(db.SmallInteger)
    volunteer = db.Column(db.SmallInteger) #志愿者报名
    comment = db.Column(db.String(100))  # 备注信息
    province = db.Column(db.SmallInteger)  # province_list 的 index #TODO 删除

    #众筹property
    payment = db.Column(db.Boolean, default=False) #F自付 T-众筹
    crowd_funding_amount = db.Column(db.Integer, default=0) #众筹金额
    crowd_funding_number = db.Column(db.Integer, default=0)  # 众筹人数
    crowd_funding_text = db.Column(db.String(500)) #众筹宣言
    supports = db.relationship('CrowdFunding', lazy='dynamic', backref=db.backref('join', lazy='joined'))  # queryd对象
    #---出行人---relationship--
    contacts = db.relationship('ActivityContact', lazy='dynamic', backref=db.backref('join', lazy='joined'))

    @staticmethod
    def get_trade_price(trade_no):
        return db.session.query(JoinActivity.price).filter(JoinActivity.trade_no == trade_no).scalar()

    @property
    def solution_obj(self):
        return ActivitySolution.query.get_or_404(self.solution)

    #TODO 之后可以去掉if
    @property
    def registration_way(self):
        if self.registration:
            return registration_way[self.registration]
        return ""

    @property
    def volunteer_name(self):
        if self.volunteer:
            return volunteer_type[self.volunteer]
        return ""

    #弃用的众筹
    @property
    def support_count(self):
        return self.supports.count()

    @property
    def supports_by_money(self):
        return self.supports.order_by('crowd_funding_details.money desc').all()


class ActivityContact(db.Model):
    __tablename__ = 'activity_contacts'

    id = db.Column(db.Integer, primary_key=True)
    join_id = db.Column(db.Integer, db.ForeignKey('join_activities.id'))
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.id'))
    name = db.Column(db.String(10))  #TODO 删除
    identity = db.Column(db.String(18)) #TODO 删除
    phone = db.Column(db.String(15)) #TODO 删除
    gender = db.Column(db.SmallInteger) #性别：0-男-1-女 #TODO 删除
    age = db.Column(db.SmallInteger) #TODO 删除

    contact = db.relationship('Contact', lazy='joined', uselist=False)



class FollowActivity(db.Model):
    __tablename__ = 'follow_activities'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())


class ActivityQuestion(db.Model):
    __tablename__ = 'activity_questions'

    id = db.Column(db.Integer, primary_key=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    question = db.Column(db.String(500), nullable=False)
    reply = db.Column(db.String(500))

    @staticmethod
    def add_question(activity, ask):
        db.session.add(ActivityQuestion(activity_id=activity.id, question=ask, user_id=current_user.id))

    def reply( self, reply):
        set.reply = reply
        db.session.add(self)


class ReviewActivity(db.Model):
    __tablename__ = 'activity_reviews'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    score = db.Column(db.SmallInteger)
    commend = db.Column(db.SmallInteger) #1-推荐 2-一般 3-不推荐
    body = db.Column(db.Text)
    reply = db.Column(db.Text)

    def reply_review(self, content):
        self.reply = content
        db.session.add(self)



class CrowdFunding(db.Model):
    __tablename__ = 'crowd_funding_details'

    #支付成功后添加数据库记录
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    join_id = db.Column(db.Integer, db.ForeignKey('join_activities.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    money = db.Column(db.Integer) #支持金额
    text = db.Column(db.String(500)) #支持宣言


