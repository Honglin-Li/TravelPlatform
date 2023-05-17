from flask_wtf import Form
from wtforms import StringField, TextAreaField, RadioField, SubmitField, ValidationError, SelectMultipleField,\
    FieldList, FormField, HiddenField, SelectField
from ..tools.field_widget import MultiCheckboxField
from wtforms.fields.html5 import DateField, IntegerField, EmailField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import Length, DataRequired, Email, Regexp, NumberRange, Optional
from ..extentions import coverPost
from ..models.outdoorType import OutdoorType
from ..models.activity import registration_way, volunteer_type, Activity
from datetime import datetime, date
from ..models.tools import province
from flask_login import current_user


class PostBaseForm(Form):
    name = StringField('帖子标题', render_kw={'placeholder': '填写标题（100字以内）', 'class': 'form-control'},
                       validators=[DataRequired('必填字段'), Length(1, 100)])
    body = TextAreaField('帖子内容(上传图片请先压缩到1M以下大小）', [DataRequired('必填字段')], render_kw={'class': 'form-control'})
    submit = SubmitField('发布帖子')


class TravelPostForm(PostBaseForm):
    cover = FileField('游记封面（建议上传宽高比2:1的封面以获得最佳浏览效果）',
                      validators=[FileAllowed(coverPost, '请上传图片格式')], render_kw={'class': 'form-control'})


class PartnerPostForm(PostBaseForm):
    start_date = DateField('出行预计开始日期', validators=[DataRequired('必填字段')], render_kw={'class': 'form-control'})
    end_date = DateField('出行预计结束日期', validators=[DataRequired('必填字段')], render_kw={'class': 'form-control'})
    days = IntegerField('计划出行天数', validators=[DataRequired('必填字段')], default=1, render_kw={'class': 'form-control'})
    destination = StringField('出行计划目的地', render_kw={'placeholder': '填写活动目的地（20字以内）', 'class': 'form-control'},
                              validators=[DataRequired('必填字段'), Length(1, 20)])


#  团队创建/编辑子论坛
class ForumForm(Form):
    name = StringField('论坛名', render_kw={'placeholder': '填写标题（64字以内）', 'class': 'form-control'},
                       validators=[DataRequired('必填字段'), Length(1, 64)])
    weight = IntegerField('权重（用于子论坛显示顺序）', default=0, render_kw={'class': 'form-control'})
    submit = SubmitField('发布帖子')


# 管理员创建社区论坛
class SNSForumForm(ForumForm):
    parent = SelectField('选择一级板块', coerce=int, render_kw={'class': 'form-control'})  # 不选择为主版块
