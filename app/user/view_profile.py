from . import user
from ..models.user import User, Contact
from flask import render_template, flash, redirect, request, url_for
from flask_login import login_required, current_user
from ..forms.profile import PhotoForm, EditProfileForm
from ..forms.activity import ContactForm
import os
from ..extentions import avatarUser, db
from ..tools.photo import resize, resize_fix_width
from ..tools.string_tools import get_rnd_filename_w_ext
from ..tools.permissions import only_user_id


@user.route('/modify_avatar', methods=['GET', 'POST'])
@login_required
def modify_avatar():
    """
    提交新头像：
        删除原头像
        resize新头像
        保存新头像(in file & database)
    :return:
    """
    form = PhotoForm()
    if form.validate_on_submit():
        if current_user.avatar:
            os.remove(avatarUser.path(filename=current_user.avatar))
        image = form.avatar.data
        imagename = get_rnd_filename_w_ext(image.filename)
        imagepath = avatarUser.path(filename=imagename)
        resize_fix_width(image, imagepath)
        current_user.avatar = imagename
        db.session.add(current_user)
        return redirect(url_for('.profile', id=current_user.id))
    return render_template('modify_avatar.html', form=form)


@user.route('/profile/<int:id>')
def profile(id):
    user = User.get_user(id)
    return render_template('profile.html', user = user)


@user.route('/profile/me')
@login_required
def profile_me():
    return redirect(url_for('.profile', id=current_user.id))


@user.route('/profile/details/<int:id>')
def profile_details(id):
    user = User.query.get_or_404(id)
    return render_template('profile_details.html', user = user)


@user.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if request.method == 'GET':
        form.username.data = current_user.username
        form.gender.data = current_user.gender
        form.birthday.data = current_user.birthday
        form.about_me.data = current_user.about_me
        form.name.data = current_user.name
        form.phone.data = current_user.phone
        form.id_number.data = current_user.id_number
        form.address.data = current_user.address
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.gender = form.gender.data
        current_user.birthday = form.birthday.data
        current_user.about_me = form.about_me.data
        current_user.phone = form.phone.data
        current_user.name = form.name.data
        current_user.id_number = form.id_number.data
        current_user.address = form.address.data
        db.session.add(current_user)
        flash('个人资料编辑成功')
        return redirect(url_for('user.profile_details', id=current_user.id))
    return render_template('edit_profile.html', form=form)

'''
---------------------关注-----------------------------
'''
@user.route('/followers/<int:id>')
def followers(id):
    page = request.args.get('page', 1, type=int)
    user = User.query.get_or_404(id)
    pagination, users = user.fans_list(page)
    return render_template('follower.html',
                           users=users,
                           user=user,
                           pagination=pagination)


#我关注的人
@user.route('/followed/<int:id>')
def followed(id):
    page = request.args.get('page', 1, type=int)
    user = User.query.get_or_404(id)
    pagination, users = user.follow_list(page)
    return render_template('followed.html',
                           users=users,
                           user=user,
                           pagination=pagination)


@user.route('/follow/<int:id>')
@login_required
def follow(id):
    user = User.query.get_or_404(id)
    current_user.follow(user)
    flash('关注成功')
    return redirect(url_for('.profile', id=id))


@user.route('/unfollow/<int:id>')
@login_required
def unfollow(id):
    user = User.query.get_or_404(id)
    current_user.unfollow(user)
    flash('取消关注成功')
    return redirect(url_for('.profile', id=id))

#-------------团队-------------
@user.route('/teams/my/<int:id>')
def my_teams(id):
    user = User.query.get_or_404(id)
    teams = user.leader_teams
    return render_template('my_teams.html',
                           user=user,
                           teams=teams)


@user.route('/teams/joined/<int:id>')
def joined_teams(id):
    user = User.query.get_or_404(id)
    teams = user.teams_joined
    return render_template('teams_joined.html',
                           user=user,
                           teams=teams)

#---------------活动-------------------
@user.route('/activities/joined/<int:id>')
def activities_joined(id):
    user = User.query.get_or_404(id)
    activities = user.activities_join()
    return render_template('activities_join.html',
                           user=user,
                           activities=activities)

@user.route('/activities/joined/unpay')
@login_required
def activities_joined_unpay():
    activities = current_user.activities_join_unpay()
    return render_template('activities_join.html',
                           user=current_user,
                           activities=activities)


@user.route('/activities/follow/<int:id>')
def activities_follow(id):
    user = User.query.get_or_404(id)
    activities = user.activities_follow()
    return render_template('activities_followed.html',
                           user=user,
                           activities=activities)

"""
出行人
"""


@user.route('/modify_contacts', methods=['GET', 'POST'])
@user.route('/modify_contacts/<int:id>', methods=['GET', 'POST'])
@login_required
def modify_contacts(id=0):
    if id:
        contact = Contact.query.get_or_404(id)
        only_user_id(contact.user_id)  # permission
    form = ContactForm()
    contacts = Contact.query.filter_by(user_id=current_user.id).all()
    if id and request.method == 'GET':
        form.real_name.data = contact.name
        form.phone.data = contact.phone
        form.gender.data = contact.gender
        form.age.data = contact.age
        form.identity.data = contact.identity
        form.province.data = contact.province
    if form.validate_on_submit():
        if not id:
            contact = Contact()
        contact.user_id = current_user.id
        contact.name = form.real_name.data
        contact.identity = form.identity.data
        contact.gender = form.gender.data
        contact.province = form.province.data
        contact.age = form.age.data
        contact.phone = form.phone.data
        db.session.add(contact)
        flash('编辑成功')
        return redirect(url_for('.modify_contacts'))
    return render_template('modify_contacts.html',
                           form=form,
                           contacts=contacts,
                           user=current_user)





