from applications.extensions import db
from datetime import datetime


# 故事测试
class Story(db.Model):
    __tablename__ = 'story'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    record = db.Column(db.Text)
    projects = db.Column(db.String(199))
    module = db.Column(db.String(199))
    status = db.Column(db.Integer, default='1')
    run_environment = db.Column(db.String(20))
    type = db.Column(db.String(10))
    create_name = db.Column(db.String(10))
    timing_configuration = db.Column(db.String(10))
    before_test = db.Column(db.Integer)
    after_test = db.Column(db.Integer)
    create_time = db.Column(db.DateTime, default=datetime.now(),comment='创建时间')
    run_time = db.Column(db.DateTime, comment='运行时间')
    username = db.Column(db.String(19))
    password = db.Column(db.String(95))
    var_dict = db.Column(db.Text, comment='故事存储的变量，用于步骤操作')
    step = db.relationship('Step', backref='Story', lazy='dynamic', cascade='all,delete-orphan')