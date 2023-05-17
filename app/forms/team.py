from flask_wtf import Form
from wtforms import (
    StringField, PasswordField, SubmitField, BooleanField, FileField, TextAreaField, SelectMultipleField,
    RadioField
)
from wtforms.validators import DataRequired, Length, ValidationError
from ..models.outdoorType import OutdoorType
from ..models.team import Team, team_type
from ..tools.field_widget import MultiCheckboxField


class TeamForm(Form):
    name = StringField('团队名称（必填）', [DataRequired('请填写团队名称名称')])
    phone = StringField('联系电话（必填，方便管理员联系，可以选择是否显示在团队首页）', [DataRequired('必填项')])
    phone_show = RadioField('联系电话是否显示在团队首页（默认显示）', coerce=int, default=1)
    description = TextAreaField('口号（选填）', [Length(max=100, message='请输入<100字的口号')])
    image = FileField('头像（选填）')
    types = MultiCheckboxField('团队活动类型（必填，按住shift键可以选择多个类型),不要忘记选择下面的团队类型',
                                [DataRequired('请选择团队类型')], coerce=int)
    classify = RadioField('团队类型', coerce=int, default=0)

    def __init__(self, *args, **kwargs):
        super(TeamForm, self).__init__(*args, **kwargs)
        self.types.choices = [(t.id, t.name) for t in OutdoorType.show_list()]
        self.classify.choices = list(enumerate(team_type))
        self.phone_show.choices = [(0, '不显示在团队首页'), (1, '显示在团队首页')]



class CreateTeamForm(TeamForm):
    document = FileField('营业执照或身份证等有效证件的扫描图片（必填）', [DataRequired('必须上传有效证件图片')])
    submit = SubmitField('创建俱乐部，半小时内审核')

    def validate_name(self, field):
        if Team.exist(field.data):
            raise ValidationError('该俱乐部名称已注册，请修改俱乐部名称')


class ModifyTeamForm(TeamForm):
    document = FileField('营业执照或身份证等有效证件的扫描图片')
    submit = SubmitField('重新提交俱乐部创建申请')

    def __init__(self,team, *args, **kwargs):
        super(ModifyTeamForm, self).__init__(*args, **kwargs)
        self.team=team

    def validate_name(self, field):
        if field.data != self.team.name and Team.exist(field.data):
            raise ValidationError('该俱乐部名称已注册，请修改俱乐部名称')


class TeamSearchForm(Form):
    keyword = StringField('搜索关键字')
    classify = RadioField('团队类型')
    outdoor = RadioField('活动类型')
    sort = RadioField('排序方式')
    submit = SubmitField('搜索团队')

    def __init__(self, *args, **kwargs):
        super(TeamSearchForm, self).__init__(*args, **kwargs)
        #为单选钮赋默认值
        self.outdoor.choices = [(item.id, item.name) for item in OutdoorType.show_list()]
        sort_source = [(0, '新成立'), (1, '最久远')] #TODO, (2, '活动最多'), (3, '会员最多')
        self.sort.choices = sort_source
        self.classify.choices = list(enumerate(team_type))



