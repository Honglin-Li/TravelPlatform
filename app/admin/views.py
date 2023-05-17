from . import admin
from flask_login import current_user, login_required
from ..forms.outdoor import CreateOutdoorTypeForm
from flask import flash, render_template, redirect, url_for, request, abort
from ..models.outdoorType import OutdoorType
from ..extentions import commonImage, db
from ..tools.string_tools import get_md5_filename
from ..decorators import admin_required
from ..models.team import Team
from ..models.demand import Demand
from ..models.user import User


@admin.route('/index')
@admin_required
def index():
    if not current_user.is_admin:
        abort(403)
    return render_template('admin_index.html')


@admin.route('/demands')
@admin_required
def demands():
    page = request.args.get('page', 1, type=int)
    pagination = Demand.get_pager(page)
    return render_template('demands.html', pagination=pagination, demands=pagination.items)


@admin.route('/users')
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    pagination = User.get_users(page)
    return render_template('admin_users.html', pagination=pagination, users=pagination.items)


@admin.route('/team_vitality')
@admin_required
def team_vitality():
    Team.query.update({Team.vitality : 1})
    flash(Team.query.first().vitality)
    return render_template('admin_index.html')


"""
已经不用的辅助功能
@admin.route('/clear-test')
@admin_required
def clear_test_user():
    from ..forgery import clear_test_user
    clear_test_user()
    return redirect(url_for('admin.users'))


@admin.route('/show-test')
@admin_required
def show_test_user():
    from ..forgery import show_test_user
    show_test_user()
    return redirect(url_for('admin.index'))


@admin.route('/gene_volunteer')
@admin_required
def gene_volunteer():
    from ..forgery import add_club
    add_club()
    return redirect(url_for('admin.index'))


@admin.route('/move_contact')
@admin_required
def move_contact():
    from ..forgery import move_contact
    move_contact()
    return redirect(url_for('admin.index'))
"""

@admin.route('/show_contact')
@admin_required
def show_contact():
    from ..models.user import Contact
    contacts = Contact.query.all()
    return render_template('show_contact.html', contacts=contacts)



