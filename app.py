#自动化测试平台，2020.5
from flask import Flask,render_template,request,url_for,redirect,flash
from flask_sqlalchemy import SQLAlchemy
import time
from flask_login import LoginManager,UserMixin,login_user,login_required,logout_user
from werkzeug.security import generate_password_hash,check_password_hash
from apitest import Test
import click

app = Flask(__name__)
login_manager = LoginManager(app)#实例化扩展类



#连接数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFCATIONS'] = False #取消对模型修改的监控
app.config['SECRET_KEY'] = 'dev'

db = SQLAlchemy(app)

#创建用例表
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
    datetime = db.Column(db.String(20))
    category = db.Column(db.String(20))
    method = db.Column(db.String(20))
    test_time = db.Column(db.String(20))
    def __init__(self,name,url,headers,data,token,content,module,before,after,state,assertion,datetime,category,method,test_time):
        self.name = name
        self.url = url
        self.headers =headers
        self.data = data
        self.token = token
        self.content = content
        self.module = module
        self.before = before
        self.after = after
        self.datetime = datetime
        self.state = state
        self.assertion = assertion
        self.category = category
        self.method = method
        self.test_time = test_time

#创建用户表
class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)

    name = db.Column(db.String(10))
    username = db.Column(db.String(10))
    password = db.Column(db.String(10))
    datetime = db.Column(db.String(20))

    def set_password(self,password):#设置密码，接受密码作为参数
        self.password = generate_password_hash(password)

    def validate_password(self,password):#验证密码

        return check_password_hash(self.password,password)#返回布尔值

db.create_all()  # 创建


#注册命令行，设置管理员账户。执行 flask admin 命令， 输入用户名和密码后，创建管理员账户。
@app.cli.command()
@click.option('--username', prompt=True, help='The username usedto login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def admin(username,password):

    user = User.query.first()
    if user is not None:
        click.echo('updating user')
        user.username = username
        user.set_password(password)#设置密码
    else:
        click.echo('creating user')
        user = User(username=username,name='admin')
        user.set_password(password)#设置密码

        db.session.add(user)
    db.session.commit()
    click.echo('Complete.')



@login_manager.user_loader
def load_user(user_id):#创建用户加载回调函数，传入用户id
    user = User.query.get(int(user_id))#查询用户
    return user


login_manager.login_view = 'login'

@app.route('/index')#首页
@login_required
def index():
    return render_template('index.html')


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':


        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('输入用户名和密码')
            return redirect(url_for('login'))

        user = User.query.first()
        #验证用户名和密码是否一样
        if username == user.username and user.validate_password(password):

            login_user(user)#登入用户
            flash('登录成功')

            return redirect(url_for('index'))#重定向至首页

        flash('用户名或密码错误')#验证不成功后提示
        return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
@login_required#视图保护
def logout():
    logout_user()#退出登录
    flash('已退出登录')
    return redirect(url_for('login'))#重定向至登录页


@app.route('/apitest')

@login_required
def apitest():
    #case = Case.query.all()
    case = Case.query.order_by(-Case.id)
    return render_template('apitest.html',case=case)


@app.route('/addtest',methods=['GET','POST'])#测试用例添加页
@login_required#登录保护，未登录时，不能访问这个页面
def addTest():
    if request.method == 'POST':
            case = Case(
            name = request.form['name'],
            url = request.form['url'],
            method = request.form['method'],
            headers = request.form['headers'],
            data = request.form['data'],
            token = request.form['token'],
            content = request.form['content'],
            module = request.form['module'],
            before = request.form['before'],
            after = request.form['after'],
            category = request.form['category'],
            assertion = request.form['assertion'],
            state = 1,
            datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),

            test_time = None,
            )

            db.session.add(case)
            db.session.commit()
            flash('添加成功')
            return redirect(url_for('apitest'))
    return render_template('addtest.html')


@app.route('/test/delete/<id>',methods=['POST'])
@login_required

def delete(id):

    case = Case.query.get_or_404(id)
    db.session.delete(case)
    db.session.commit()
    flash('操作成功')
    return redirect(url_for('apitest'))

#编辑页
@app.route('/test/edit/<int:id>',methods=['GET','POST'])
@login_required
def edit(id):
    case = Case.query.get_or_404(id)

    if request.method =='POST':
        #获取浏览器发送的数据
        case.name = request.form['name']
        case.url = request.form['url']
        case.headers = request.form['headers']
        case.data = request.form['data']
        case.token = request.form['token']
        case.content = request.form['content']
        case.module = request.form['module']
        case.category = request.form['category']
        case.before = request.form['before']
        case.after = request.form['after']
        case.assertion = request.form['assertion']
        #写入表中提交
        db.session.commit()
        flash('修改成功')
        #重定向至测试用例管理页
        return redirect(url_for('apitest'))
    return render_template('edit.html',case=case)

@app.route('/task')
@login_required
def task():
    return render_template('task.html')


@app.route('/add_task')
@login_required
def addTask():
    return render_template('addtask.html')


@app.route('/result_manage')
@login_required
def resultMange():#测试报告管理
    return render_template('resultmanage.html')


@app.route('/result')
@login_required
def result():
    return '测试报告'

@app.route('/user_manage')
def userMange():
    return render_template('user_manage.html')



@app.route('/add_user')
@login_required
def addUser():
    return '添加用户'



@app.route('/help')
@login_required
def help():

    return render_template('help.html')



@app.route('/run<int:id>')
@login_required
def run(id):
    case = Case.query.get_or_404(id)
    #获取测试数据
    name = case.name
    url =case.url
    headers = case.headers
    data = case.data
    token = case.token
    content = case.content
    method = case.method
    before = case.before
    after = case.after
    assertion = case.assertion
    category = case.category


    test = Test()
    if test.test_api(url=url,method=method,headers=headers,data=data,assertion=assertion) is True:
        case.state = '2'#2是测试通过，3是不通过，1是未测试

        case.test_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    else:
        case.state = '3'
        case.test_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    db.session.commit()
    flash('已运行')
    return redirect(url_for('apitest'))


if __name__ == '__main__':
    app.run()

    #app.run(debug=True)

