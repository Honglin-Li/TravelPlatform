from . import team
from flask import redirect, flash, render_template, url_for, request, session, abort
from ..models.activity import (
    Activity,
    JoinActivity,
    ActivityContact,
    ActivityQuestion,
    CrowdFunding,
    ActivitySolution,
    RegistrationWay,
    Volunteer,
    registration_way,
    volunteer_type)
from ..models.team import Team, TeamJoinActivity
from ..models.outdoorType import OutdoorType
from ..models.user import User, Contact
from flask_login import login_required, current_user
from ..forms.activity import (
    CreateActivityForm,
    ActivityContactsForm,
    ActivityAskForm,
    ContactForm,
    CrownSupportForm,
    ActivitySearchForm,
    ActivitySolutionForm,
    ActivityVolunteerJoinForm,
    ActivityTeamJoinForm)
from ..tools.string_tools import get_md5_filename_w_ext, trans_html, get_rnd_filename_w_ext
from ..tools.photo import cut, qrcode_img, qrcode_cover, resize
from ..extentions import coverPost, db
import datetime
from ..tools.permissions import only_team_admin, only_team_available, only_self, only_user_id


"""
编辑活动
"""


def fill_activity(activity, form, new=False, club=None):
    if new:
        activity.created_by = current_user.id
        activity.belong_to_team = club.id
    activity.name = form.name.data
    activity.start_date = form.start_date.data
    activity.end_date = form.end_date.data
    activity.days = (activity.end_date - activity.start_date).days + 1
    activity.rally_site = form.rally_site.data
    activity.destination = form.destination.data
    activity.price = form.price.data
    activity.child_price = form.child_price.data if form.child_price.data else 0
    activity.maximum = form.maximum.data
    activity.intensity_index = form.intensity_index.data
    activity.landscape_index = form.landscape_index.data
    activity.phone = form.phone.data
    activity.registration = sum(form.registration_way.data)  # 注册方式直接求和
    activity.types = [OutdoorType.query.get(item) for item in form.travel_type.data]
    activity.introduce = trans_html(form.introduce.data)
    activity.team_join_info = form.team_letter.data
    cover = form.cover.data
    if cover:
        filename = get_rnd_filename_w_ext(cover.filename)
        resize(cover, coverPost.path(filename), width=1200)
        activity.cover = filename
    return activity


@team.route('/activity/add/<int:id>', methods=['GET', 'POST'])
@login_required
def create_activity(id):
    group = Team.query.get_or_404(id)
    only_team_available(group)
    only_team_admin(group, current_user)
    form = CreateActivityForm()
    if form.validate_on_submit():
        activity = Activity()
        activity = fill_activity(activity, form, True, group)
        db.session.add(activity)
        #group.add_vitality(5)  # 添加活跃度
        db.session.add(group)
        db.session.commit()
        flash('活动发布成功，您可以选择添加多个活动方案')
        return redirect(url_for('.activity_add_sln', id = activity.id))
    return render_template('activity_add.html', form=form)


@team.route('/activity/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_activity(id):
    activity = Activity.query.get_or_404(id)
    only_team_available(activity.team)
    only_team_admin(activity.team, current_user)
    form = CreateActivityForm(activity=activity)
    if request.method == 'GET':
        #填充数据
        form.name.data = activity.name
        form.start_date.data = activity.start_date
        form.end_date.data = activity.end_date
        form.rally_site.data = activity.rally_site
        form.destination.data = activity.destination
        form.price.data = activity.price
        form.maximum.data = activity.maximum
        form.intensity_index.data = activity.intensity_index
        form.landscape_index.data = activity.landscape_index
        form.phone.data = activity.phone
        form.introduce.data = activity.introduce
        form.registration_way.data = [way for way in registration_way if way & activity.registration] #位操作符
        form.travel_type.data = [t.id for t in activity.types]
    if form.validate_on_submit():
        activity = fill_activity(activity, form)
        db.session.add(activity)
        db.session.commit()
        flash('活动更新成功成功，您可以选择继续维护活动方案')
        return redirect(url_for('.activity_add_sln', id = activity.id))
    return render_template('activity_add.html', form=form)


@team.route('/activity/sln/<int:id>', methods=['GET', 'POST'])
@login_required
def activity_add_sln(id):
    activity = Activity.query.get_or_404(id)
    only_team_admin(activity.team, current_user)
    form = ActivitySolutionForm()
    if form.validate_on_submit():
        if form.sln_id.data:
            #更新
            sln = ActivitySolution.query.get_or_404(int(form.sln_id.data))
            sln.edit(form.name.data, form.detail.data)
        # 新建
        else:
            ActivitySolution.add_solution(activity, form.name.data, form.detail.data)
        return redirect(url_for('.activity_add_sln', id=id))
    return render_template('activity_add_solutions.html',
                           activity=activity,
                           solutions = activity.solutions,
                           form=form)


@team.route('/activity/sln/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_sln(id):
    sln = ActivitySolution.query.get_or_404(id)
    activity_id=sln.activity.id
    db.session.delete(sln)
    return redirect(url_for('.activity_add_sln', id=activity_id))


@team.route('/activity/delete/<int:id>')
@login_required
def delete_activity(id):
    activity = Activity.query.get_or_404(id)
    only_team_available(activity.team)
    only_team_admin(activity.team, current_user)
    db.session.delete(activity)
    flash('活动已删除')
    return redirect(url_for('.team_index', id=current_user.leader_team.id))

"""
活动页
"""


@team.route('/activity/<int:id>', methods=['GET', 'POST'])
def activity(id):
    activity = Activity.query.get_or_404(id)
    activity.view()
    form = ActivityAskForm()
    #handle ask
    solutions = activity.solutions if activity.solotion_count else None #这里如果直接不判断直接用activity.solotions，不是空，是查询对象
    if form.validate_on_submit():
        ask = form.ask.data
        ActivityQuestion.add_question(activity, ask)
        flash('提问成功，已通知队长，请等候回复')
        return redirect(url_for('team.activity', id=id))
    return render_template('activity.html', activity=activity, form=form, solutions=solutions)

"""
关注取消关注-关注活动列表
"""
#TODO 取消关注
@team.route('/activity/follow/<int:id>')
def follow(id):
    activity = Activity.query.get_or_404(id)
    activity.follow(current_user)
    flash('关注成功')
    return redirect(url_for('.activity', id=id))


#TODO 分页
@team.route('/activities/follow/')
@team.route('/activities/follow/<int:id>')
def activities_follow(id=0):
    user = User.get_user(id)
    activities = user.activities_follow()
    return render_template('activities_follow.html', activities = activities)


"""
报名
"""


# 个人/志愿者/团队成员报名
@team.route('/activity/join/<int:id>', methods=['GET', 'POST'])
@login_required
def activity_join(id):
    team_id = request.args.get('team_id', 0, type=int)
    volunteer = request.args.get('volunteer', 0, type=int)
    activity = Activity.query.get_or_404(id)
    if volunteer:
        form = ActivityVolunteerJoinForm(solutions=activity.solutions.all())  # 针对志愿者生成单选出行人表单
    else:
        form = ActivityContactsForm(solutions=activity.solutions.all())
    contact_form = ContactForm()
    if form.submit.data and form.validate():
        #报名
        contacts = form.contact_source.data
        sln = form.solution.data
        comment = form.comment.data
        child_count = form.child_count.data if isinstance(form, ActivityContactsForm) and form.child_count.data else 0  #志愿者报名没有儿童
        count = len(contacts) if isinstance(contacts, list) else 1
        if child_count > count:
            child_count = count
            flash('您填写的儿童人数大于选中人数，已经将儿童人数调整为总人数，如果有误，请修改信息')
        join = activity.sign_up(child_count, contacts, sln, comment, team_id, volunteer=volunteer)
        return redirect(url_for('team.activity_confirm', id=join.id))
    if contact_form.add.data and contact_form.validate():
        #添加出行人
        contact = Contact(
            user_id = current_user.id,
            name = contact_form.real_name.data,
            identity = contact_form.identity.data,
            phone = contact_form.phone.data,
            gender = contact_form.gender.data,
            province = contact_form.province.data,
            age = contact_form.age.data
        )
        db.session.add(contact)
        return redirect(url_for('.activity_join',id=id, team_id=team_id, volunteer=volunteer))
    return render_template('activity_join.html', form=form, contact_form=contact_form)


#编辑报名信息
@team.route('/activity/join/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def activity_join_edit(id):
    join = JoinActivity.query.get_or_404(id)
    only_user_id(join.user_id) #仅当前用户可访问
    activity = join.activity
    if activity.past:
        flash('活动已结束，不能修改')
        return redirect(url_for('.activity', id=join.activity_id))
    form = ActivityVolunteerJoinForm(solutions=activity.solutions.all()) \
        if join.registration == RegistrationWay.VOLUNTEER else ActivityContactsForm(solutions=activity.solutions.all())
    contact_form = ContactForm()
    if request.method == 'GET':#如果POST回传错误，也会执行继续添加联系人
        form.solution.data = join.solution
        form.comment.data = join.comment
        if isinstance(form, ActivityContactsForm):
            form.child_count.data = join.child_count
        form.contact_source.data = join.contacts[0].contact_id \
            if join.registration == RegistrationWay.VOLUNTEER else [item.contact_id for item in join.contacts]
    if form.validate_on_submit():
        contacts = form.contact_source.data
        sln = form.solution.data
        comment = form.comment.data
        child_count = form.child_count.data if isinstance(form, ActivityContactsForm) and form.child_count.data else 0  # 志愿者报名没有儿童
        join = activity.join_edit(child_count, contacts, sln, comment, join)
        flash('修改成功')
        return redirect(url_for('team.activity_confirm', id=join.id))
    return render_template('activity_join.html', form=form, contact_form=contact_form)


#修改团队报名信息
@team.route('/activity/join_team/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def activity_team_join_edit(id):
    join = TeamJoinActivity.query.get_or_404(id)
    only_team_admin(join.team, current_user)
    form = ActivityTeamJoinForm(join.activity.solutions.all())
    if request.method == 'GET':
        form.phone.data = join.phone
        form.price.data = join.team_price
        form.solution.data = join.solution
        form.child_price.data = join.child_price
        form.team_content.data = join.team_content
    if form.validate_on_submit():
        join.phone = form.phone.data
        join.team_price = form.price.data
        join.child_price = form.child_price.data
        join.team_content = form.team_content.data
        join.solution = form.solution.data
        db.session.add(join)
        flash('修改成功')
        return redirect(url_for('.activity_index_team', id=join.id))
    return render_template('activity_join_team.html', form=form)


#取消团队报名
@team.route('/activity/join_team/cancel/<int:id>')
@login_required
def activity_team_join_cancel(id):
    join = TeamJoinActivity.query.get_or_404(id)
    only_team_admin(join.team, current_user)
    if TeamJoinActivity.get_member_count(join.team_id, join.activity_id):
        flash('已经有会员报名了该活动，您不能取消该活动')
        abort(403)
    db.session.delete(join)
    flash('取消团队报名')
    return redirect(url_for('index'))


#确认订单
@team.route('/activity/join_confirm/<int:id>', methods=['GET', 'POST'])
@login_required
def activity_confirm(id):
    #订单详细信息
    join = JoinActivity.query.get_or_404(id)
    team = request.args.get('team', 0, type=int)
    qrcode = ""
    if join.registration == RegistrationWay.TEAM:
        qrcode = TeamJoinActivity.get_qrcode(join.team_id, join.activity_id)
    """form = CrownSloganForm()#注释掉的众筹信息
    if form.validate_on_submit():
        join.crowd_funding_text = form.slogan.data
        db.session.add(join)
        return redirect(url_for('team.crowd_funding_index', id=join.id))"""
    return render_template('activity_confirm.html', join=join, team=team, qrcode=qrcode)


#取消报名
@team.route('/activity/join/cancel/<int:id>')
@login_required
def activity_cancel(id):
    join = JoinActivity.query.get_or_404(id)
    if join.state:
        flash('您已经付款，请联系领队取消活动')
    else:
        db.session.delete(join)
        flash('您已取消参与该活动')
    return redirect(url_for('index'))


#查看报名明细---主活动+报名活动的团队管理员查看本团队报名情况
@team.route('/activity/join/details/<int:id>')
@login_required
def activity_join_details(id):
    activity = Activity.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    team_id = request.args.get('team_id', 0, type=int)
    if team_id:
        team = Team.query.get_or_404(team_id)
        only_team_admin(team, current_user)
    else:
        only_team_admin(activity.team, current_user)
    details = Activity.get_registration_details(activity.id, team_id=team_id)
    return render_template('activity_registration_details.html',
                           contacts=details)


#团队报名
@team.route('/activity/join/team/<int:id>', methods=['GET', 'POST'])
@login_required
def activity_join_team(id):
    #没有团队的会员点入
    if not current_user.is_leader:
        flash('先创建团队，才能在报名的时候选择团队报名哦~')
        return redirect(url_for('team.create_team'))
    activity = Activity.query.get_or_404(id)
    form = ActivityTeamJoinForm(activity.solutions.all())
    if request.method == 'GET':
        form.phone.data = current_user.phone
        form.price.data = activity.price
        form.child_price.data = activity.child_price
    if form.validate_on_submit():
        team_id = current_user.leader_team.id
        join = activity.join_team(team_id,
                                  form.phone.data,
                                  form.solution.data if form.solution.data else None,
                                  form.price.data,
                                  form.child_price.data,
                                  form.team_content.data)
        flash('团队报名成功')
        if activity.team_join_info:
            return render_template('team_letter.html',
                                   content=activity.team_join_info,
                                   id=join.id)
        return redirect(url_for('.activity_index_team', id=join.id))
    return render_template('activity_join_team.html', form=form)


#团队报名的活动主页
@team.route('/activity/team_join/<int:id>', methods=['GET', 'POST'])
def activity_index_team(id):
    join = TeamJoinActivity.query.get_or_404(id)
    return render_template('activity_team_join.html',
                           join=join)


@team.route('/activity/gene_qrcode/<int:id>')
def gene_qrcode(id):
    activity = Activity.query.get_or_404(id)
    activity.qrcode = activity.gene_qrcode()
    db.session.add(activity)
    flash('已重新生成二维码，请查看')
    return redirect(url_for('.activity', id=activity.id))


#团队报名的活动列表
@team.route('/activities/team_join/<int:id>')
def activitys_team_join(id):
    team = Team.query.get_or_404(id)
    activities = team.get_activities_joined()
    return render_template('activities_team_join.html',
                           activities=activities,
                           team=team)

'''
取得各种活动列表
'''


#团队活动
@team.route('/activities/team/<int:id>')
def activities_team(id):
    team = Team.query.get_or_404(id)
    activities = team.activities.order_by('activities.timestamp desc').all()
    return render_template('activities_team.html', activities=activities, team=team)


#活动搜索
@team.route('/activites/search', methods=['GET', 'POST'])
def activities_search():
    form = ActivitySearchForm()
    page = request.args.get('page', 1, type=int)
    if request.method == 'POST':
        #每次POST，添加查询字符串，取回第一页
        session['activity-keyword'] = form.keyword.data
        session['activity-outdoor'] = form.outdoor.data
        session['activity-days'] = form.days.data
        session['activity-sort'] = form.sort.data
        page = 1
    pagination = Activity.get_activities_search(
        session.get('activity-keyword', ""),
        session.get('activity-outdoor', 'None'),
        session.get('activity-days', 'None'),
        session.get('activity-sort', 'None'),
        page
    )
    activities = pagination.items
    return render_template('activities_search.html',
                           form=form,
                           activities = activities,
                           pagination = pagination)


@team.route('/activites/search/home')
def activities_search_home():
    #需要重置session
    session['activity-keyword'] = ""
    session['activity-outdoor'] = 'None'
    session['activity-days'] = 'None'
    session['activity-sort'] = 'None'
    return redirect(url_for('.activities_search'))


#主页活动分类点入的
@team.route('/activities/search/<int:id>')
def activities_search_with_outdoor(id):
    if OutdoorType.query.filter_by(id=id).count:
        session['activity-outdoor'] = str(id)
        #清空其他session
        session['activity-keyword'] = ""
        session['activity-days'] = 'None'
        session['activity-sort'] = 'None'
        return redirect(url_for('.activities_search'))
    else:
        flash('您选择的活动分类不存在')



"""
暂时不用的众筹页面
"""

@team.route('/crowd_funding/index/<int:id>')
def crowd_funding_index(id):     #TODO 众筹分享页面
    join = JoinActivity.query.get_or_404(id)
    percentage = int(join.crowd_funding_amount / join.price * 100) if int(join.crowd_funding_amount / join.price) < 1 else 100
    return render_template('crowd_funding_index.html', join=join, percentage=percentage)


@login_required
@team.route('/crowd_funding/support/<int:id>', methods=['GET', 'POST'])
def crowd_funding_support(id):
    join = JoinActivity.query.get_or_404(id)
    form = CrownSupportForm()
    if form.validate_on_submit():
        #TODO 付款成功再添加数据记录
        support = CrowdFunding()
        support.user_id = current_user.id
        support.join = join
        support.text = form.text.data
        support.money = form.money.data
        support.join.crowd_funding_number += 1
        support.join.crowd_funding_amount += support.money
        db.session.add(support)
        flash('支持成功，谢谢您的支持')
        return redirect(url_for('team.crowd_funding_index', id=join.id))
    return render_template('crowd_funding_support.html', form=form, join=join)










