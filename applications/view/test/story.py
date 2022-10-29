from flask import render_template, request, url_for, redirect, Blueprint, flash, jsonify
from applications.models import Story, Step, TestRecord
from applications.common.utils.rights import authorize
from applications.view.test.utils.apitest import test_api
from applications.view.test.utils.function import getValue, substitution_variable, str_to_list, expression_value
import time
from applications.extensions import db
from .form.scene import Register, Add

story = Blueprint('story', __name__, url_prefix='/story')


@story.route('/', defaults={'page': 1})
@story.route('/page/<int:page>/', methods=['get'])
@authorize("story:story_manage:main", log=True)
def manage(page):
    per_page = 10
    pagination = Story.query.order_by(-Story.id).paginate(page, per_page=per_page)
    story = pagination.items

    return render_template('test/scene.html', pagination=pagination, storys=story)


@story.route('/add/', methods=['get', 'post'])
def add():
    form = Add()
    if request.method == 'POST':
        if form.validate_on_submit():
            st = Story(
                name = form.name.data,
                projects = form.project.data,
                var_dict = form.var_dict.data
            )
            db.session.add(st)
            db.session.commit()
            return redirect(url_for('story.manage'))
    return render_template('test/add_scene.html', form=form)


@story.route('/run/', methods=['get'])
def run():
    story_id = request.args.get('story_id')
    story = Story.query.filter_by(id=story_id).first()
    step_list = Step.query.filter_by(story_id=story.id).all()
    var_dict = story.var_dict

    try:

        varDict = eval(var_dict) # 字符串转换为字典
    except Exception:
        varDict = {}
    story_status = []
    for step in step_list:

        url = step.url
        data = step.request_data
        method = step.method
        username = step.username
        step_name = step.name
        password = step.password
        assertion = step.assertion
        expression = step.expression
        environment = step.environment
        project = step.project
        var_name = step.var_name

        if method.upper() in ['GET', 'PATCH', 'PUT'] and '{' in url:
            url = substitution_variable(var_dict=varDict, url=url)

        elif method.upper() == 'POST':
            url = substitution_variable(var_dict=varDict, url=url)
            data_dict = eval(data)
            print(data_dict)
            data = substitution_variable(var_dict=varDict, data=data_dict)

        if environment == '测试':
            if project == '新奥e保后台':
                url = f'https://api-test.ennejb.cn{url}'
        else:
            if project == '后台系统':
                url = f'https://api.ennejb.cn{url}'

        try:
            request_header, request_data, res_data = test_api(url=url, projects=project,
                                                                  environment=environment,
                                                                  method=method, data=data, username=username,
                                                                  password=password, story=True)
        except Exception:
            return jsonify({"code": 400, "message":f"步骤运行异常,检查步骤: {step_name} {url} {data}"})

        create_time = time.strftime("%Y-%m-%d %H:%M", time.localtime())
        response_dict = res_data[0]
        # print(response_dict)
        expression = str_to_list(expression) # 转换为列表
        print(url, request_header)
        r = expression_value(response=response_dict, expression = expression)

        varDict[var_name] = r # 变量名和值存入到字典

        db.session.query(Story).filter(Story.id == story_id).update({'var_dict': f'{varDict}'}) # 更新表

        if type(r) == int or type(r) == float:
            r = str(r)
            if r == assertion:
                state = '通过'  # 一致，通过

            else:
                state = '不通过'  # 不通过

        elif r == assertion:
            state = '通过'  # 一致，通过

        elif assertion == 'None':
            state = '通过'

        elif assertion == 'None':
            if r is None:
                state = '通过'
            else:

                state = '不通过'
        else:

            state = '不通过'  # 不通过

        # 保存测试记录
        task_record = TestRecord(
            step_id=step.id,
            case_name=step.name,
            state=state,
            request_header=str(request_header),
            request_data=str(request_data),
            res_data=str(res_data),
            create_time=create_time,
        )

        db.session.query(Step).filter(Step.id == step.id).update({'status': state})
        db.session.add(task_record)
        db.session.commit()



        story_status.append(step.status)
    if '不通过' in story_status:
        db.session.query(Story).filter(Story.id == story_id).update({'status': 2})
    else:
        db.session.query(Story).filter(Story.id == story_id).update({'status': 1})

    db.session.query(Story).filter(Story.id == story_id).update({'run_time': create_time})
    db.session.commit()
    print(story_status)
    return jsonify({"message":"运行完成"})


@story.route('/register', methods=['get', 'post'])
def register():
    form = Register()
    if request.method == 'POST':
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            print(username)
            print(password)
            print(type(form.data))
            print(form.data)
            return "success"
        else:
            print(form.errors)
            error_msg = form.errors
            for k, v in error_msg.items():
                print(k, v[0])
            return "重新填写"
    return render_template('test/form.html', form=form)


@story.route('/delete/<int:story_id>', methods=['GET'])
def delete(story_id):
    story_id = Story.query.get_or_404(story_id)
    db.session.delete(story_id)
    db.session.commit()
    flash('操作成功')
    return redirect(url_for('story.manage' ))


@story.route('/edit/<int:story_id>', methods=['get'])
def edit(story_id):
    story = Story.query.get_or_404(story_id)
    return render_template('test/edit_story.html', story=story)


@story.route('/step/<int:story_id>', methods=['get'])
def step(story_id):
    step = Step.query.filter_by(story_id=story_id)
    story = Story.query.get_or_404(story_id)
    return render_template('test/story_step.html',steps=step,story_id=story_id, var_dict = story.var_dict)



@story.route('/add_step/<int:story_id>', methods=['get', 'post'])
def add_step(story_id):
    if request.method == 'POST':
        step = Step(

            name=request.form['name'],
            project=request.form['projects'],
            url=request.form['url'],
            story_id = story_id,
            method=request.form['method'],
            assertion=request.form['assertion'],
            expression=request.form['expression'],
            var_name=request.form['var'],
            request_data=request.form['data'],
            username=request.form['username'],
            password=request.form['password'],
            environment=request.form['environment']
        )

        db.session.add(step)
        db.session.commit()
        # return redirect(url_for('story.step',story_id=story_id))
        return jsonify({"message":"已增加步骤"})
    return render_template('test/add_step.html', story_id=story_id)


@story.route('/delete_step/<int:step_id>', methods=['get'])
def delete_step(step_id):
    step = Step.query.get_or_404(step_id)
    db.session.delete(step)
    db.session.commit()
    return jsonify({"message":"已删除"})


@story.route('/edit_step/<int:step_id>', methods=['get','post'])
def edit_step(step_id):
    step = Step.query.get_or_404(step_id)

    if request.method == 'POST':

        step.name = request.form['name'],
        step.project = request.form['project'],
        step.url = request.form['url'],
        step.method = request.form['method'],
        step.assertion = request.form['assertion'],
        step. expression = request.form['expression'],
        step.var_name = request.form['var'],
        step.request_data = request.form['data'],
        step.username = request.form['username'],
        step.password = request.form['password'],
        step.environment = request.form['environment']
        db.session.commit()
        return jsonify({"message":"已修改"})
    return render_template('test/edit_step.html', step=step)