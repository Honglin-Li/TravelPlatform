"""
CLASS Team:

CLASS TEAM_USERS
"""
from ..extentions import db, avatarTeam, imgTeam
from datetime import datetime
from .outdoorType import team_types
from .activity import Activity
from .outdoorType import OutdoorType
from flask import current_app, url_for
from sqlalchemy.sql.expression import and_
from ..tools.photo import qrcode_url_string, qrcode_cover
from ..extentions import coverPost


"""
团队类型
以索引形式访问
e.g. team_type[0]
"""
team_type = (
    '俱乐部团队',
    '志愿者团队',
    '文娱团队'
)


class Team(db.Model):
    __tablename__ = 'teams'

    def __repr__(self):
        return '<Team %r>' % self.name

    #property:basic
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    leader_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    classify = db.Column(db.SmallInteger, default=0)  # 团队分类
    phone = db.Column(db.String(15))  # 团队必须有联系方式
    phone_show = db.Column(db.Boolean, default=True) #联系电话是否显示在首页
    vitality = db.Column(db.Integer, default=0)  # 活跃度

    #property:admin
    approved = db.Column(db.Boolean, default=False) #首次申请俱乐部 需要审批
    unapproved_cause = db.Column(db.String(100))#审核未通过答复
    disabled = db.Column(db.Boolean, default=False) #禁言or other

    #property:info
    description = db.Column(db.String(100))
    bulletin = db.Column(db.String(500))
    cover = db.Column(db.String(128)) #TODO 暂时不用，日后扩展
    avatar = db.Column(db.String(128))
    document = db.Column(db.String(128)) #营业执照 身份证等有效证件
    qrcode = db.Column(db.String(128))

    #property:type
    types = db.relationship('OutdoorType', secondary=team_types, backref=db.backref('teams', lazy='dynamic'))

    # --------------------------------------------------image-----------------------------------
    @property
    def classify_type(self):
        return team_type[self.classify]

    @property
    def avatar_url(self):
        filename = self.avatar if self.avatar else 'default-team.jpg'
        return avatarTeam.url(filename=filename)

    @property
    def cover_url(self):
        filename = self.cover if self.cover else 'default.jpg'
        return imgTeam.url(filename=filename)

    @property
    def document_url(self):
        return imgTeam.url(self.document)

    @staticmethod
    def get_team_name_by_id(team_id):
        return db.session.query(Team.name).filter(Team.id==team_id).scalar()

    #返回可以显示的团队
    @property
    def available(self):
        return self.approved and (not self.disabled)

    #----------admin--------
    def add_vitality(self, vitality=1):
        if not vitality:
            vitality=0
        self.vitality += vitality

    def approve(self):
        self.approved = True
        db.session.add(self)

    def unapprove(self, cause):
        self.unapproved_cause = cause
        db.session.add(self)

    def lock(self):
        self.disabled = True
        db.session.add(self)

    def unlock(self):
        self.disabled = False
        db.session.add(self)

    @staticmethod
    def exist(team_name):
        return Team.query.filter_by(name=team_name).count()

    @staticmethod
    def exist_id(id):
        return Team.query.filter_by(id=id).count()

    @staticmethod
    def access(id):
        return Team.query.filter_by(and_(id=id, approved=True, disabled=False)).count()

    def is_admin(self, user):
        if user.is_anonymous:
            return False
        return TeamUser.query.filter(and_(TeamUser.user_id==user.id, TeamUser.team_id==self.id,
                                          TeamUser.is_admin==True)).count()

    @property
    def administrator(self):
        return [item.user for item in self.team_members.filter_by(is_admin=True).all()]


    #-------------------------------会员-----------------------------------------------
    team_members = db.relationship('TeamUser', backref=db.backref('team', lazy='joined'),
                              lazy='dynamic', cascade='all, delete-orphan')

    def members(self, page=1):
        pagination = self.team_members.order_by(TeamUser.timestamp.desc()
                                                ).paginate(page, current_app.config['PAGECOUNT_TEAM'],
                                                           error_out=False)
        members = [item.user for item in pagination.items]
        return pagination, members

    @property
    def member_count(self):
        return self.team_members.count()

    def get_top_members(self, count=5):
        return [item.user for item in self.team_members.limit(count).all()]

    def join(self, user, is_admin=False):
        if not self.is_member(user):
            relation = TeamUser(team=self, user=user, is_admin=is_admin)
            self.add_vitality()
            db.session.add(relation)

    @staticmethod
    def join_team(user_id, team_id, is_admin=False):
        if Team.exist_id(team_id) and (not Team.is_member_static(user_id, team_id)):
            relation = TeamUser(team_id=team_id, user_id=user_id, is_admin=is_admin)
            db.session.add(relation)
            return True
        return False


    @staticmethod
    def quit_team(user_id, team_id):
        relation = TeamUser.query.filter_by(team_id=team_id, user_id=user_id).first()
        if relation and (not relation.is_admin):
            db.session.delete(relation)
            return True
        return False

    @staticmethod
    def is_member_static(user_id, team_id):
        return TeamUser.query.filter_by(team_id=team_id, user_id=user_id).count()

    def is_member(self, user):
        return user.is_authenticated and self.team_members.filter_by(user_id=user.id).count()

    def is_leader(self, user):
        return user.is_authenticated and user.id == self.leader_id

    # -------------------------------各种获取团队的方法---分页-----------------------------------------------
    @staticmethod
    def get_teams_unapproved():
        return Team.query.filter_by(approved=False).order_by(Team.timestamp.desc()).all()

    @staticmethod
    def get_teams_disabled():
        return Team.query.filter_by(disabled=True).order_by(Team.timestamp.desc()).all()

    @staticmethod
    def get_teams_search(keyword, outdoor, classify, sort, page=1):
        teams = Team.query
        if outdoor != 'None':  # 户外类型
            t = OutdoorType.query.get(int(outdoor))
            teams = t.teams
        if keyword:  # 允许多个空格分隔的搜索关键字
            keywords = keyword.split()
            for k in keywords:
                teams = teams.filter(Team.name.like('%' + k + '%'))
        if classify != 'None':  # 团队类型
            teams = teams.filter(Team.classify == int(classify))
        if sort != 'None':  # 排序
            if sort == '1':
                teams = teams.order_by(Team.timestamp.asc())
            #TODO  按照活动数和会员数排序
            else: #默认排序为新成立
                teams = teams.order_by(Team.timestamp.desc())
        return teams.paginate(page, current_app.config['PAGECOUNT_TEAM'], error_out=False)


    #query for show
    #---------------------------活动-------------------------------------
    activities = db.relationship('Activity', lazy='dynamic', backref= db.backref('team', lazy='joined'))
    activities_joined = db.relationship('TeamJoinActivity', lazy='dynamic', backref=db.backref('team', lazy='joined'))

    def get_activities_joined(self):
        #TODO 分页
        return [(item.id, item.activity) for item in self.activities_joined.order_by(TeamJoinActivity.timestamp.desc()).all()]

    @property
    def activity_count(self):
        return self.activities.count()

    def get_top_activities(self, top=5):
        return self.activities.order_by(Activity.timestamp.desc()).limit(top).all()




class TeamUser(db.Model):
    __tablename__ = 'team_users'
    def __repr__(self):
        return '<TeamUser %r>' % self.team_id

    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    #----管理功能----
    is_admin = db.Column(db.Boolean, default=False) #俱乐部管理员
    title = db.Column(db.String(10)) #团内称号  eg财务主管 队长
    disabled = db.Column(db.Boolean, default=False) #在本群内禁言

    @property
    def title_show(self):
        if self.title:
            return self.title
        if self.user_id == self.team.leader_id:
            return "队长"
        if self.is_admin:
            return "管理员"
        return "会员"



"""
辅助类，为了方便取数据，JoinActivity来回取数太麻烦
"""
class TeamJoinActivity(db.Model):
    __tablename__ = 'team_join_activities'

    def __repr__(self):
        return '<TeamJoinActivity %r>' % self.team_id

    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    team_price = db.Column(db.Integer)
    child_price = db.Column(db.SmallInteger)
    phone = db.Column(db.String(15))
    team_content = db.Column(db.String(500))
    qrcode = db.Column(db.String(128))
    solution = db.Column(db.SmallInteger)

    @property
    def qrcode_url(self):
        return qrcode_url_string(self.qrcode)

    @staticmethod
    def get_item(team_id, activity_id):
        return TeamJoinActivity.query.filter_by(team_id=team_id, activity_id=activity_id).first()

    @staticmethod
    def get_price(team_id, activity_id):
        return db.session.query(TeamJoinActivity.team_price).filter(TeamJoinActivity.team_id==team_id,
                                                                    TeamJoinActivity.activity_id==activity_id).scalar()

    @staticmethod
    def get_child_price(team_id, activity_id):
        return db.session.query(TeamJoinActivity.child_price).filter(TeamJoinActivity.team_id == team_id,
                                                                    TeamJoinActivity.activity_id == activity_id).scalar()

    #TODO 分页
    def members(self):
        from .activity import JoinActivity
        return JoinActivity.query.filter_by(team_id=self.team_id, activity_id=self.activity_id).all()

    @property
    def member_count(self):
        from .activity import JoinActivity
        return JoinActivity.query.filter_by(team_id=self.team_id, activity_id=self.activity_id).count()

    @staticmethod
    def get_member_count(team_id, activity_id):
        from .activity import JoinActivity
        return JoinActivity.query.filter_by(team_id=team_id, activity_id=activity_id).count()

    @staticmethod
    def get_id(team_id, activity_id):
        return TeamJoinActivity.query.filter_by(team_id=team_id, activity_id=activity_id).first()

    @staticmethod
    def get_qrcode(team_id, activity_id):
        return db.session.query(TeamJoinActivity.qrcode).filter(TeamJoinActivity.team_id==team_id, TeamJoinActivity.activity_id==activity_id).scalar()

    def gene_qrcode(self):
        if self.cover:
            img = qrcode_cover(url_for('team.activity_index_team', id=self.id, _external=True), coverPost.path(self.cover))
        else:
            img = qrcode_cover(url_for('team.activity_index_team', id=self.id, _external=True), coverPost.path('default.jpg'))
        return img







