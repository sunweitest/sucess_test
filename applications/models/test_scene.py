from applications.extensions import db
from datetime import datetime


# 多接口测试用例
class Scene(db.Model):
    __tablename__ = 'scene'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    record = db.Column(db.Text)
    case_list = db.Column(db.Text)
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
    assertion = db.Column(db.Text)
    category = db.Column(db.Text)



