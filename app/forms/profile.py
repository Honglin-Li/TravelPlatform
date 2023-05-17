from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FileField, RadioField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError, Optional
from wtforms.fields.html5 import DateField, IntegerField
from ..tools.photo import resize
from ..models.user import User
from flask_login import current_user


class PhotoForm(Form):
    avatar = FileField('选择图片：', [DataRequired('请选择图片')])
    submit = SubmitField('上传图片')


class EditProfileForm(Form):
    #头像
    username = StringField('用户名', validators=[Length(1, 64, '只能输入64个字符以内哦')])
    gender = RadioField('性别', choices=[('男', '男'), ('女', '女'), ('不告诉你', '不告诉你')])
    birthday = DateField('出生日期', [Optional()])
    about_me = TextAreaField('个性签名', [Length(0, 100, '只能输入100字以内哦')])
    #出行+邮寄信息
    name = StringField('真实姓名', validators=[Length(0, 64, '最多只能输入64个字符哦')])
    phone = StringField('电话', validators=[Length(0, 15,'请输入正确的手机号')])
    id_number = StringField('身份证号', validators=[Length(0, 18, '身份证号只能是18位哦')]) #TODO正则表达式
    address = StringField('地址', validators=[Length(0, 64, '地址只能是64字以内')])
    submit = SubmitField('保存')


    def validate_username(self, field):
        if self.username.data != current_user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('该用户名已注册，你可以换个其他的用户名')

    def validate_phone(self, field):
        if self.phone.data != current_user.phone and User.query.filter_by(phone=field.data).first():
            raise ValidationError('该电话已注册，你可以换个其他的电话')

