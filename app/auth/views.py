"""
view list:
login()
logout()
"""
from . import auth
from ..forms.login import LoginForm, RegisterForm, ChangePasswordForm, ForgetPasswordForm, ValidationEmailForm
from flask import render_template, flash, redirect, request, url_for
from flask_login import login_user, logout_user, current_user, login_required
from ..models.user import User
from .. import db
from ..extentions import send_msg


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    用户登陆
    :return:跳转or错误信息
    """
    form = LoginForm()
    form_forget = ValidationEmailForm()
    if form.submit.data and form.validate_on_submit():
        user = User.query.filter_by(phone=form.account.data).first() or User.query.filter_by(username=form.account.data).first() \
               or User.query.filter_by(email=form.account.data).first()
        if user:
            if user.verify_password(form.password.data):
                if not user.lock:
                    login_user(user, remember=form.remember_me.data)
                    return redirect(request.args.get('next') or url_for('index'))
                else:
                    flash('您的账户已被锁定，请与管理员联系')
            else:
                flash('密码输入错误，请重试')
        else:
            flash('手机号/用户名/邮箱不存在，请注册')
    elif form_forget.goto_email.data and form_forget.validate_on_submit():
        #发送邮件
        to = [form_forget.email.data]
        title = '【小猫游园】忘记密码'
        template = 'forget_pwd'
        user = User.query.filter_by(email=form_forget.email.data).first()
        pwd = User.get_rnd_password()
        user.password = pwd
        db.session.add(user)
        send_msg(to=to, title=title, template=template, pwd=pwd)
        return redirect(url_for('auth.login'))
    return render_template('login.html', form=form, form2=form_forget)


@auth.route('/logout')
@login_required
def logout():
    """
    用户注销
    :return:跳转到主页
    """
    logout_user()
    flash('您已退出登陆')
    return redirect(url_for('index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, password=form.password.data)
        user.email = form.email.data or None
        user.phone = form.phone.data or None
        db.session.add(user)
        db.session.commit()
        user.follow(user)  # 关注自己
        db.session.add(user)
        flash('注册成功，您现在可以登陆了')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form= form)


@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.password = form.password.data
        db.session.add(current_user)
        flash('密码修改成功')
        return redirect(url_for('user.profile', id=current_user.id))
    return render_template('change_password.html', form=form)


@auth.route('/forget_password', methods=['GET', 'POST'])
def forget_password():
    form = ForgetPasswordForm()
    if form.validate_on_submit():
        token = request.args.get('token')
        username = User.get_username(token)
        if username:
            user = User.query.filter_by(username=username).first()
            user.password = form.password.data
            db.session.add(user)
            flash('密码重置成功,请重新登陆')
        else:
            flash('重置失败，请重试')
        return redirect(url_for('auth.login', id=current_user.id))
    return render_template('forget_password.html', form=form)



