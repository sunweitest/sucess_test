from applications.extensions import db


# 测试记录表
class TestRecord(db.Model):
    __tablename__ = 'testrecord'
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer)
    case_name = db.Column(db.String(20))
    task_id = db.Column(db.Integer, db.ForeignKey('testtask.id', ondelete='CASCADE'))
    run_id = db.Column(db.Integer, default='1')
    state = db.Column(db.String(10))
    request_header = db.Column(db.Text)
    request_data = db.Column(db.Text)
    res_data = db.Column(db.Text)
    create_time = db.Column(db.DateTime, comment='创建时间')
    step_id = db.Column(db.Integer)