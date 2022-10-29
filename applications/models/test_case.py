from applications.extensions import db


# 用例表
class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    url = db.Column(db.String(100))
    headers = db.Column(db.Text)
    data = db.Column(db.Text)
    token = db.Column(db.String(100))
    module = db.Column(db.String(100))
    before = db.Column(db.String(100))
    after = db.Column(db.String(100))
    state = db.Column(db.String(10))
    assertion = db.Column(db.Text)
    datetime = db.Column(db.DateTime, comment='创建时间')
    category = db.Column(db.Text)
    method = db.Column(db.String(20))
    test_time = db.Column(db.DateTime, comment='创建时间')
    projects = db.Column(db.String(20))
    environment = db.Column(db.String(10))
    create_name = db.Column(db.String(10))
    mobile = db.Column(db.String(11))
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))
    request_header = db.Column(db.Text)
    request_data = db.Column(db.Text)
    res_data = db.Column(db.Text)
    case_sql = db.Column(db.Text)

# 接口表
class Api(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    url = db.Column(db.String(100))
    headers = db.Column(db.Text)
    data = db.Column(db.Text)
    token = db.Column(db.String(100))
    method = db.Column(db.String(9))
    create_time = db.Column(db.DateTime, comment='创建时间')
    updata_time = db.Column(db.DateTime, comment='更新时间')
    api_history = db.relationship('ApiHistory', backref='Api', lazy='dynamic', cascade='all,delete-orphan')

class ApiHistory(db.Model):
    __tablename__ = "api_history"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    url = db.Column(db.String(100))
    headers = db.Column(db.Text)
    data = db.Column(db.Text)
    token = db.Column(db.String(100))
    method = db.Column(db.String(9))
    create_time = db.Column(db.DateTime, comment='创建时间')

    api_id = db.Column(db.Integer, db.ForeignKey('api.id', ondelete='CASCADE'))