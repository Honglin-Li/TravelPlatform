from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email,ValidationError, Length, Regexp, EqualTo, Optional
from ..models.user import User
from wtforms.fields.html5 import EmailField

class LoginForm(Form):
    account = StringField('手机号/用户名/邮箱：', validators=[DataRequired("没有填写手机号或用户名"), Length(1,64, '请正确填写')])
    password = PasswordField('密码', validators=[DataRequired('必填项')])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登陆')


class ValidationEmailForm(Form):
    email = EmailField('邮箱(必填）', validators=[Email('请正确填写邮箱'), DataRequired('必填')])
    goto_email = SubmitField('前往邮箱查看临时密码进行登陆')

    def validate_email(self, field):
        if not User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱未注册')


class RegisterForm(Form):
    username = StringField('用户名', validators=[DataRequired('请填写用户名'), Length(1, 64)],
                           render_kw={'placeholder':'必填，可以用用户名、手机号、邮箱登陆'})
    phone = StringField('手机号（选填）', validators=[Optional(), Length(0, 15, '请填写正确格式的手机号')], render_kw={'placeholder': '选填，用于忘记密码重置密码，建议填写'})
    email = EmailField('邮箱（选填）', validators=[Optional(),Email('请正确填写邮箱')], render_kw={'placeholder': '选填'})
    password = PasswordField('密码', validators=[DataRequired('请填写密码'), EqualTo('confirmPassword', message='密码不一致')])
    confirmPassword = PasswordField('再次输入密码', validators=[DataRequired('请确认密码')])
    submit = SubmitField('注册')

    def validate_phone(self, field):
        if User.query.filter_by(phone=field.data).first():
            raise ValidationError('该手机号已注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱已注册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('该用户名已注册')


class ChangePasswordForm(Form):
    oldPassword = PasswordField('旧密码', [DataRequired('请输入旧密码')])
    password = PasswordField('密码', validators=[DataRequired('请填写密码'), EqualTo('confirmPassword', message='密码不一致')])
    confirmPassword = PasswordField('再次输入密码', validators=[DataRequired('请确认密码')])
    submit = SubmitField('修改密码')


class ForgetPasswordForm(Form):
    password = PasswordField('密码', validators=[DataRequired('请填写密码'), EqualTo('confirmPassword', message='密码不一致')])
    confirmPassword = PasswordField('再次输入密码', validators=[DataRequired('请确认密码')])
    submit = SubmitField('修改密码')

