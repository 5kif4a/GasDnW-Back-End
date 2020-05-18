from datetime import datetime

from api.utils import LevelType
from .flask_app import db


class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.Text)

    mq2_data = db.relationship('MQ2Data', backref='device')
    dht_data = db.relationship('DHTData', backref='device')

    def __repr__(self):
        return f'<Device: id: {self.id} - Location: {self.location}>'

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=True)
    date_time = db.Column(db.DateTime, default=datetime.now)
    note = db.Column(db.Text, nullable=False)
    level = db.Column(db.Enum(LevelType), nullable=False)

    mq2_data = db.relationship('MQ2Data', backref='case')
    dht_data = db.relationship('DHTData', backref='case')

    report = db.relationship('Report', backref='case')
    notification = db.relationship('Notification', backref='case')

    def __repr__(self):
        return f'<Case: DateTime: {self.date_time} - Level: {self.level}>'

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class MQ2Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.DateTime, default=datetime.now)
    lpg = db.Column(db.Integer, nullable=False)
    co = db.Column(db.Integer, nullable=False)
    smoke = db.Column(db.Integer, nullable=False)

    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'))

    def __repr__(self):
        return f'<MQ2Data: DateTime: {self.date_time} - LPG: {self.lpg} - CO: {self.co} - Smoke: {self.smoke}' \
               f' - Device: {self.device_id}> '

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class DHTData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.DateTime, default=datetime.now)
    temp = db.Column(db.Integer, nullable=False)
    hudimity = db.Column(db.Integer, nullable=False)

    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'))

    def __repr__(self):
        return f'<DHTData: DateTime: {self.date_time} - Temperature: {self.temp} - Hudimity: {self.hudimity}>'

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Camera(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.Text)

    camera = db.relationship('Log', backref='camera')

    def __repr__(self):
        return f'<Camera: id: {self.id} - Location: {self.location}>'

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=True)
    date_time = db.Column(db.DateTime, default=datetime.now)
    camera_id = db.Column(db.Integer, db.ForeignKey('camera.id'))
    recognized_objects = db.Column(db.Text, nullable=True)

    report = db.relationship('Report', backref='log')
    notification = db.relationship('Notification', backref='log')

    def __repr__(self):
        return f'<Log: DateTime {self.date_time} - Camera: {self.camera}>'

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    content = db.Column(db.Text)

    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=True)
    log_id = db.Column(db.Integer, db.ForeignKey('log.id'), nullable=True)

    def __repr__(self):
        return f'<Report: DateTime: {self.created_at} - Content: {self.content}>'

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.DateTime, default=datetime.now)
    content = db.Column(db.Text)

    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=True)
    log_id = db.Column(db.Integer, db.ForeignKey('log.id'), nullable=True)

    def __repr__(self):
        return f'<Notification: DateTime: {self.date_time}>'

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.DateTime, default=datetime.now)
    endpoint = db.Column(db.Text)
    expiration_time = db.Column(db.Text, nullable=True)
    p256dh = db.Column(db.Text)
    auth = db.Column(db.Text)

    def __repr__(self):
        return f'<Subscriber: id: {self.id} - Token: {self.token}>'

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
