"""
CLASS OutdoorType

Talble team_types

Talble activity_types
"""
from ..extentions import db
from datetime import datetime
from ..extentions import commonImage


class OutdoorType(db.Model):
    __tablename__ = 'outdoor_types'
    def __repr__(self):
        return '<Outdoor Type %r>' % self.name

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), unique=True, index=True, nullable=False)
    image = db.Column(db.String(128))
    disabled = db.Column(db.Boolean, default=False)
    weight = db.Column(db.SmallInteger, default=0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    #禁用分类，不在主页显示
    def disable(self):
        self.disabled = True
        db.session.add(self)

    def show(self):
        self.disabled = False
        db.session.add(self)

    @property
    def image_url(self):
        return commonImage.url(filename=self.image)

    @staticmethod
    def show_list():
        return OutdoorType.query.filter_by(disabled=False).order_by(OutdoorType.weight.desc()).all()

    @staticmethod
    def admin_list():
        return OutdoorType.query.all()


team_types = db.Table('team_types',
                      db.Column('team_id', db.Integer, db.ForeignKey('teams.id'), primary_key=True),
                      db.Column('type_id', db.Integer, db.ForeignKey('outdoor_types.id'), primary_key=True))


activity_types = db.Table('activity_types',
                          db.Column('activity_id', db.Integer, db.ForeignKey('activities.id'), primary_key=True),
                          db.Column('type_id', db.Integer, db.ForeignKey('outdoor_types.id'), primary_key=True))
