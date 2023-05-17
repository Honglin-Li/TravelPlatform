from flask_wtf import Form
from wtforms import StringField, TextAreaField, RadioField, SubmitField, ValidationError, SelectMultipleField,\
    FieldList, FormField
from wtforms.fields.html5 import DateField, IntegerField
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import Length, DataRequired, Email, Regexp, NumberRange
from ..extentions import coverPost
from ..models.outdoorType import OutdoorType
from datetime import datetime, date


class DemandForm(Form):
    company = StringField('公司名称（必填）', [DataRequired('必填项'), Length(1,50, '最多只能填50字哦')])
    contact = StringField('联系人（必填）', [DataRequired('必填项'), Length(1,50, '最多只能填50字哦')])
    phone = StringField('联系方式（必填）', [DataRequired('必填项'), Length(1,15, '最多只能填50字哦')])
    image = TextAreaField('形象展示需求(选填）', [Length(max=1000, message="最多只能输入1000个字")])
    brand = TextAreaField('品牌推广需求(选填）', [Length(max=1000, message="最多只能输入1000个字")])
    product = TextAreaField('产品销售需求(选填）', [Length(max=1000, message="最多只能输入1000个字")])
    market = TextAreaField('占领市场需求(选填）', [Length(max=1000, message="最多只能输入1000个字")])
    other = TextAreaField('其他需求(选填）', [Length(max=1000, message="最多只能输入1000个字")])
    submit = SubmitField('提交您的需求')
