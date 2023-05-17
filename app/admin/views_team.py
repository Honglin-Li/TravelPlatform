from . import admin
from flask_login import current_user, login_required
from ..forms.outdoor import CreateOutdoorTypeForm
from flask import flash, render_template, redirect, url_for, request, abort
from ..models.outdoorType import OutdoorType
from ..extentions import commonImage, db
from ..tools.string_tools import get_md5_filename
from ..decorators import admin_required
from ..models.team import Team
from ..models.activity import Activity
from ..forms.admin import ApproveTeamForm


"""
团队详细页+审核不通过
"""


@admin.route('/team/<int:id>', methods=['GET', 'POST'])
@admin_required
def team(id):
    team = Team.query.get_or_404(id)
    form = ApproveTeamForm()
    if request.method == 'GET':
        form.cause.data = team.unapproved_cause
    if form.validate_on_submit():
        cause = form.cause.data
        team.unapprove(cause)
        flash('成功提交不审核原因')
        return redirect(url_for('.unapprove_team_list'))
    return render_template('team_admin.html', form=form, team=team)

"""
团队审批
"""


@admin.route('/teams_unapproved')
@admin_required
def unapprove_team_list():
    teams = Team.get_teams_unapproved()
    return render_template('team_approve.html', teams=teams)


@admin.route('/team_approve/<int:id>')
@admin_required
def approve_team(id):
    team = Team.query.get_or_404(id)
    team.approve()
    flash('审核通过')
    return redirect(url_for('.unapprove_team_list'))

"""
团队封号解封
"""


@admin.route('/team_lock/<int:id>')
@admin_required
def lock_team(id):
    team = Team.query.get_or_404(id)
    team.lock()
    flash('团队已封号')
    return redirect(url_for('.locked_team_list'))


@admin.route('/team_unlock/<int:id>')
@admin_required
def unlock_team(id):
    team = Team.query.get_or_404(id)
    team.unlock()
    flash('团队已解封')
    return redirect(url_for('.locked_team_list'))


@admin.route('/teams_locked')
@admin_required
def locked_team_list():
    teams = Team.get_teams_disabled()
    return render_template('team_disable.html', teams=teams)

"""
置顶活动
"""


@admin.route('/activities')
@admin_required
def activities():
    page = request.args.get('page', 1, type=int)
    pagination = Activity.get_activities(page)
    return render_template('top_activities.html',
                           pagination=pagination,
                           activities=pagination.items)


@admin.route('/activity/top<int:id>')
@admin_required
def top(id):
    activity = Activity.query.get_or_404(id)
    if not activity.top:
        activity.top = True
        db.session.add(activity)
        flash('置顶成功')
    return redirect(url_for('.activities'))


@admin.route('/activity/un_top<int:id>')
@admin_required
def un_top(id):
    activity = Activity.query.get_or_404(id)
    if activity.top:
        activity.top = False
        db.session.add(activity)
        flash('取消置顶成功')
    return redirect(url_for('.activities'))


@admin.route('/activity/delete<int:id>')
@admin_required
def delete_activity(id):
    activity = Activity.query.get_or_404(id)
    db.session.delete(activity)
    flash('活动删除成功')
    return redirect(url_for('.activities'))
