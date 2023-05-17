from . import pay
from ..extentions import alipay, db
from flask import url_for, current_app, redirect, request, session, render_template, flash
import json
from ..models.activity import JoinActivity
from datetime import datetime
from flask_login import current_user


# 用户完成支付，GET回调
@pay.route('/alipay')
def paid():
    #想alipay发起查询
    out_trade_no = request.args.get('out_trade_no')
    join = JoinActivity.query.filter_by(trade_no=out_trade_no).first_or_404()
    result = alipay.api_alipay_trade_query(out_trade_no=out_trade_no)
    if result.get("trade_status", "") == "TRADE_SUCCESS":
        # 处理join信息
        if join.price == int(float(result.get('total_amount'))):
            join.alipay_no = result.get('trade_no')
            join.state = True
            db.session.add(join)
            return render_template('success.html')
    return render_template('fail.html')


# 发起支付 id=join_id，从AJ中取出价格等支付信息
# 暂时只支持活动付款
@pay.route('/start_pay/<int:id>')
def start_alipay(id):
    from urllib.parse import urlencode
    join = JoinActivity.query.get_or_404(id)
    if not join.trade_no:
        join.trade_no = datetime.now().strftime('%Y%m%d%H%M%S') + str(current_user.id)
        db.session.add(join)
    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=join.trade_no,
        total_amount=join.price,
        subject='小猫游园活动',
        return_url=url_for('.paid', _external=True)
    )
    alipay_url = current_app.config['ALIPAY_URL'] + "?" + order_string
    return redirect(alipay_url)

