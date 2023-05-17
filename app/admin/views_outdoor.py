from . import admin
from flask_login import current_user, login_required
from ..forms.outdoor import CreateOutdoorTypeForm
from flask import flash, render_template, redirect, url_for, request, abort
from ..models.outdoorType import OutdoorType
from ..extentions import commonImage, db
from ..tools.string_tools import get_md5_filename
from ..decorators import admin_required


@login_required
@admin_required
@admin.route('/edit_outdoor_type', methods=['GET', 'POST'])
@admin.route('/edit_outdoor_type/<int:id>', methods=['GET', 'POST'])
def edit_outdoor_type(id=0):
    #TODO 装饰器
    if not current_user.is_admin:
        abort(403)
    form = CreateOutdoorTypeForm()
    collection = OutdoorType.admin_list()
    item = OutdoorType()
    if id != 0:
        item = OutdoorType.query.get_or_404(id)
        #将GET和0两个条件写在一行会导致无法编辑，因为编辑是POST，未加载item，导致更新变new，数据库重复记录
        if request.method == 'GET':
            form.name.data = item.name
            form.weight.data = item.weight
    if form.validate_on_submit():
        item.name = form.name.data
        item.weight = form.weight.data
        file = form.image.data
        if file:
            item.image = commonImage.save(file, folder='outdoor_type',
                                          name=get_md5_filename(current_user.username) + '.')
        db.session.add(item)
        return redirect(url_for('.edit_outdoor_type'))
    return render_template('edit_outdoor_type.html', form=form, collection=collection)


@login_required
@admin_required
@admin.route('/disable_outdoor/<int:id>')
def disable_outdoor(id):
    t = OutdoorType.query.get_or_404(id)
    t.disable()
    return redirect(url_for('.edit_outdoor_type'))


@login_required
@admin_required
@admin.route('/disable_outdoor/<int:id>')
def show_outdoor(id):
    t = OutdoorType.query.get_or_404(id)
    t.show()
    return redirect(url_for('.edit_outdoor_type'))

