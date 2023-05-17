from flask import url_for, flash, redirect, abort
from ..models.team import Team
from flask_login import current_user


#团队权限问题
def only_team_admin(team, user):
    if not (team.is_admin(user) or user.is_admin):
        flash('当前操作只有团队管理员或网站管理员可以使用')
        abort(403)


def only_team_available(team):
    if not team.available:
        flash('您的团队尚未审核，或被封号，当前不能进行任何操作')
        abort(403)


#本人才能操作
def only_self(user):
    if user != current_user:
        flash('必须本人才能进行该操作')
        abort(403)


def only_user_id(user_id):
    if user_id != current_user.id:
        flash('必须本人才能进行该操作')
        abort(403)

