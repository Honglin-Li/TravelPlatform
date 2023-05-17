from functools import wraps
from flask import abort
from flask_login import current_user
from flask import flash, redirect, url_for
from .models.team import Team
from sqlalchemy.sql.expression import and_


#-管理员可访问---必须在最内层
def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return func(*args, **kwargs)
    return wrapper


#只允许正常团队使用该功能------有问题未启用
def team_available(id):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if Team.query.filter_by(and_(id=id, approved=True, disabled=False)).count():
                flash('该团队暂时不能访问')
                return redirect(url_for('index'))
            return func(*args, **kwargs)
        return wrapper
    return decorator
