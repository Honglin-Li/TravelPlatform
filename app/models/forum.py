from ..extentions import db
from datetime import datetime, timedelta
from flask_login import current_user
from flask import current_app, flash, session, url_for
import re


class PostClassify:
    SNS = 0  # 主贴
    Travel = 1  # 游记攻略
    Partner = 2  # 结伴


#  二级社区
class Forum(db.Model):
    __tablename__ = 'forums'

    def __repr__(self):
        return '<Forum %r>' % self.name

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('forums.id'))  # 2级分类
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String('64'))
    weight =  db.Column(db.Integer, default=0)
    vitality = db.Column(db.Integer, default=0)
    # TODO avatar description


#  团队讨论区
class TeamForum(db.Model):
    __tablename__ = 'team_forums'

    def __repr__(self):
        return '<TeamForum %r>' % self.name

    id = db.Column(db.Integer, primary_key=True)
    sns_id = db.Column(db.Integer, db.ForeignKey('forums.id'))  # 2级分类 挂接主论坛，暂时不用
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    name = db.Column(db.String('64'))
    weight = db.Column(db.Integer, default=0)


#  帖子
class Post(db.Model):
    __tablename__ = 'posts'

    def __repr__(self):
        return '<Post %r>' % self.title

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    sns_id = db.Column(db.Integer, db.ForeignKey('forums.id'))  # 社区帖子
    team_sns_id = db.Column(db.Integer, db.ForeignKey('team_forums.id'))  # 团队讨论区帖子
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))  # 团队讨论区帖子
    activity_id = db.Column(db.Integer, db.ForeignKey('activites.id'))  # 活动的游记
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    classify = db.Column(db.SmallInteger, default=0)  # 0-主论坛 1- 游记攻略 2-结伴游
    title = db.Column(db.String('100'))
    body = db.Column(db.Text)
    cover = db.Column(db.String(128))  # 所有游记攻略的封面
    destination = db.Column(db.String(50))  # 结伴-目的地
    start_date = db.Column(db.DateTime, nullable=False)  # 结伴-开始时间
    end_date = db.Column(db.DateTime, nullable=False)  # 结伴-结束时间
    days = db.Column(db.SmallInteger)  # 结伴 天数
    top = db.Column(db.Boolean, default=False)  # 社区置顶-管理员可用
    top_team = db.Column(db.Boolean, default=False)  # 版面置顶-版主可用
    viewcount = db.Column(db.Integer, default=0)
    essence = db.Column(db.Boolean, default=False)  # 精华帖
