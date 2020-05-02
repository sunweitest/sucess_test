
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

#链接数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
#app.config['SQLALCHEMY_TRACK_MODIFCATIONS'] = False #取消对模型修改的监控
#app.config['SECRET_KEY'] = 'dev'

db = SQLAlchemy(app)


class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    url = db.Column(db.String(100))
    headers = db.Column(db.String(100))
    data = db.Column(db.String(1000))
    token = db.Column(db.String(100))
    content = db.Column(db.String(100))
    module = db.Column(db.String(100))
    before = db.Column(db.String(100))
    after = db.Column(db.String(100))
    state = db.Column(db.String(100))
    assertion = db.Column(db.String(100))
    def __init__(self,name,url,headers,data,token,content,module,before,after,state,assertion):
        self.name = name
        self.url = url
        self.headers =headers
        self.data = data
        self.token = token
        self.content = content
        self.module = module
        self.before = before
        self.after = after

        self.state = state
        self.assertion =assertion

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(20))






db.create_all()#创建