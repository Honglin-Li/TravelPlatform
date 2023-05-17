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


class ApproveTeamForm(Form):
    cause = TextAreaField('审核不通过的原因', [DataRequired('必填项'), Length(max=100, message="最多只能输入100个字")])
    submit = SubmitField('审核不通过')
