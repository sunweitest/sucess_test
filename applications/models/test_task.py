from applications.extensions import db


# 任务表
class TestTask(db.Model):
    __tablename__ = 'testtask'
    id = db.Column(db.Integer, primary_key=True)
    task_name = db.Column(db.String(20))
    case_list = db.Column(db.Text)
    projects = db.Column(db.String(199))
    module = db.Column(db.String(199))
    task_status = db.Column(db.Integer, default='1')
    run_environment = db.Column(db.String(20))
    task_type = db.Column(db.String(10))
    create_name = db.Column(db.String(10))
    timing_configuration = db.Column(db.String(10))
    accept_mail = db.Column(db.String(20))
    task_list = db.Column(db.Text)
    create_time = db.Column(db.DateTime, comment='创建时间')
    run_time = db.Column(db.DateTime, comment='运行时间')
    test_record = db.relationship('TestRecord', backref='TestTask', lazy='dynamic', cascade='all,delete-orphan')