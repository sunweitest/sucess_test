from applications.extensions import db
from datetime import datetime


# 故事测试的步骤
class Step(db.Model):
    __tablename__ = 'step'

    id = db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.Integer, db.ForeignKey('story.id', ondelete='CASCADE'))
    name = db.Column(db.String(98))
    project = db.Column(db.String(19))
    method = db.Column(db.String(9))
    url = db.Column(db.String(100))
    create_name = db.Column(db.String(10))
    before_test = db.Column(db.Text)
    after_test = db.Column(db.Text)
    assertion = db.Column(db.Text)
    expression = db.Column(db.String(199), comment='表达式')
    var_name = db.Column(db.String(19))
    username = db.Column(db.String(19))
    password = db.Column(db.String(95))
    res_data = db.Column(db.Text)
    case_sql = db.Column(db.Text)
    request_data = db.Column(db.Text)
    environment = db.Column(db.String(10))
    status = db.Column(db.Enum('未运行', '通过', '不通过'))
    create_time = db.Column(db.DateTime, default=datetime.now(),comment='创建时间')
    run_time = db.Column(db.DateTime, comment='运行时间' )