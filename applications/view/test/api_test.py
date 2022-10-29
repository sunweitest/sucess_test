from flask import render_template, request, url_for, redirect, flash, Blueprint
from applications.view.test.utils.apitest import test_api
from applications.view.test.utils.function import getValue, substitution_variable, expression_value, str_to_list
from applications.common.utils.rights import authorize
from applications.models import Case
import time
from applications.extensions import db


test_bp = Blueprint('smart_test', __name__, url_prefix='/smart_test')


@test_bp.route('/apitest', defaults={'page': 1})
@test_bp.route('/apitest/page/<int:page>')
@authorize("smart_test:apitest:caselist", log=True)
def apitest(page):
    per_page = 16
    pagination = Case.query.order_by(-Case.id).paginate(page, per_page=per_page)  # 分页对象
    case = pagination.items  # 当前页数的记录列表
    return render_template('test/test_manage.html', pagination=pagination, case=case)


@test_bp.route('/addtest', methods=['GET', 'POST'])  # 测试用例添加页
@authorize("smart_test:addtest:main", log=True)
def add_test():
    if request.method == 'POST':
        case = Case(
            name=request.form['name'],
            url=request.form['url'],
            method=request.form['method'],
            headers=request.form['headers'],
            data=request.form['data'],
            token=request.form['token'],
            environment=request.form['environment'],
            module=request.form['module'],
            before=request.form['before'],
            after=request.form['after'],
            category=request.form['category'],
            assertion=request.form['assertion'],
            state=1,
            datetime=time.strftime("%Y-%m-%d %H:%M", time.localtime()),
            projects=request.form['projects'],
            test_time=None,
            username=request.form['username'],
            password=request.form['password'],
            create_name=request.form['create_name']
        )
        db.session.add(case)
        db.session.commit()
        flash('新增成功')
        return redirect(request.referrer) # 返回到上一链接
    return render_template('test/add_test.html')


@test_bp.route('/test/delete/<case_id>', methods=['POST'])
def delete(case_id):
    case = Case.query.get_or_404(case_id)
    db.session.delete(case)
    db.session.commit()
    flash('操作成功')

    return redirect(url_for('smart_test.apitest'))


# 编辑页
@test_bp.route('/test/edit/<int:case_id>', methods=['GET', 'POST'])
def edit(case_id):
    case = Case.query.get_or_404(case_id)

    if request.method == 'POST':
        # 获取浏览器发送的数据
        case.name = request.form['name']
        case.url = request.form['url']
        case.headers = request.form['headers']
        case.data = request.form['data']
        case.environment = request.form['environment']
        case.module = request.form['module']
        case.category = str(request.form['category'])
        case.before = request.form['before']
        case.after = request.form['after']
        case.assertion = request.form['assertion']
        case.projects = request.form['projects']
        # case.token = request.form['token']
        case.username = request.form['username']
        case.password = request.form['password']
        case.method = request.form['method']

        # 写入表中提交
        db.session.commit()

        flash('修改成功')

        # 重定向至测试用例管理页
        return redirect(url_for('smart_test.apitest'))
    return render_template('test/edit.html', case=case)


@test_bp.route('/run/<int:id>/')
def run(id):
    case = Case.query.get_or_404(id)
    # 获取测试数据
    url = case.url
    data = case.data
    username = case.username
    password = case.password
    method = case.method
    assertion = case.assertion
    category = case.category
    environment = case.environment
    projects = case.projects
    module = case.module
    import time


    if environment == '测试':
        url = substitution_variable(var_dict=None, url=url)
        url = f'https://api_test.com{url}'
    elif environment == '线上':

        url = f'https://api.com{url}'

    print('开始接口测试', url)

    request_header, request_data, res_data = test_api(url=url, projects=projects, environment=environment,
                                                      method=method, data=data, username=username, password=password)

    case.test_time = time.strftime("%Y-%m-%d %H:%M", time.localtime())

    # 获取预期结果，和实际结果对比
    r = res_data[0]
    # r = getValue(r, category)  # 获取要断言的参数的值
    expression = str_to_list(category)  # 转换为列表
    r = expression_value(response=r, expression=expression)
    print(r, assertion)
    print(type(r),type(assertion))
    if type(r) == int or type(r) == float:
        r = str(r)
        if r == assertion:
            case.state = '2'  # 一致，通过
        else:
            case.state = '3'  # 不通过

    elif r == assertion:
        case.state = '2'  # 一致，通过

    elif assertion == 'None':
        if r is None:
            case.state = '2'
        else:
            case.state = '3'

    else:
        case.state = '3'  # 不通过

    case.request_header = str(request_header)
    case.request_data = str(request_data)
    case.res_data = str(res_data)

    db.session.commit()

    flash('已运行')
    return redirect(url_for('smart_test.apitest'))


@test_bp.route('/log/<int:id>', methods=['GET'])
def log(id):
    case = Case.query.filter_by(id=id).first()
    return render_template('test/log.html', header=case.request_header, body=case.request_data,
                           data=case.res_data, name=case.name, url=case.url,
                             time=case.test_time)