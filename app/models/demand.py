from ..extentions import db
from datetime import datetime
from flask import current_app


class Demand(db.Model):
    __tablename__ = 'demands'

    def __repr__(self):
        return '<Demand %r>' % self.company

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    company = db.Column(db.String(50), index=True, nullable=False)
    contact = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    image = db.Column(db.String(1000))
    brand = db.Column(db.String(1000))
    product = db.Column(db.String(1000))
    market = db.Column(db.String(1000))
    other = db.Column(db.String(1000))

    @staticmethod
    def get_pager(page=1):
        return Demand.query.order_by(Demand.timestamp.desc()).paginate(page,
                                                                       current_app.config['PAGECOUNT_COMMON'],
                                                                       False)

