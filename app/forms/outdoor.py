from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FileField, IntegerField
from wtforms.validators import DataRequired


class CreateOutdoorTypeForm(Form):
    name = StringField('类型',[DataRequired('类型名称必填')])
    weight = IntegerField('排序',default=0)
    image = FileField('图片')
    submit = SubmitField('创建户外分类')

