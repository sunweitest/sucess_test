from applications.extensions import db


# 报告表
class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    report_name = db.Column(db.String(60))
    task_id = db.Column(db.Integer)
    # 1、全部通过 2、部分通过 3
    run_id = db.Column(db.Integer)
    report_status = db.Column(db.Integer)
    case_count = db.Column(db.Integer)
    test_success = db.Column(db.Integer)
    test_fail = db.Column(db.Integer)
    skip_test = db.Column(db.Integer)
    create_name = db.Column(db.String(10))
    create_time = db.Column(db.DateTime, comment='创建时间')

