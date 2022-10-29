from flask import render_template, request, url_for, redirect, Blueprint, flash, jsonify
from sqlalchemy import desc
from applications.models import TestTask, Report, TestRecord, Case
from applications.common.utils.rights import authorize
from applications.view.test.utils.apitest import test_api
from applications.view.test.utils.function import getValue, substitution_variable,  expression_value, str_to_list
import time
from applications.extensions import db
import logging

test_task_bp = Blueprint('test_task', __name__, url_prefix='/test_task')


@test_task_bp.route('/task_manage', defaults={'page': 1})
@test_task_bp.route('/task_manage/page/<int:page>')
@authorize("test_task:task_manage:main", log=True)
def task_manage(page):
    per_page = 10
    pagination = TestTask.query.order_by(-TestTask.id).paginate(page, per_page=per_page)
    test_task = pagination.items
    return render_template('test/task_manage.html', pagination=pagination, test_task=test_task)


@test_task_bp.route('/add_task', methods=['POST', 'GET'])
def add_task():
    if request.method == 'POST':
        task = TestTask(
            task_type=request.form['task_type'],
            task_name=request.form['task_name'],
            run_environment=request.form['run_environment'],
            projects=','.join(request.form.getlist('projects')),
            timing_configuration=request.form['timing_configuration'],
            create_name=request.form['create_name'],
            accept_mail=request.form['accept_mail'],
            create_time=time.strftime("%Y-%m-%d %H:%M", time.localtime()),

        )
        db.session.add(task)
        db.session.commit()
        return redirect(url_for('test_task.task_manage'))
    return render_template('test/add_task.html')


@test_task_bp.route('/run_task/<int:task_id>/')
def run_task(task_id):

    task = TestTask.query.filter_by(id=task_id).first()

    projects = task.projects.split(',')
    record = TestRecord.query.filter_by(task_id=task_id).order_by(-TestRecord.id).first()
    try:
        run_num = record.run_id
        run_num += 1

    except Exception:
        run_num = 1

    for i in projects:
        id_list = db.session.query(Case.id).filter_by(projects=i).all()
        for id in id_list:
            case = Case.query.filter_by(id=id[0]).first()
            url = case.url
            data = case.data
            method = case.method
            username = case.username
            password = case.password
            assertion = case.assertion
            category = case.category
            environment = case.environment
            projects = case.projects
            print(case.name)

            if environment == '测试':
                url = substitution_variable(var_dict=None, url=url)
                url = f'https://api-test.ennejb.cn{url}'
            else:
                url = substitution_variable(var_dict=None, url=url)
                url = f'https://api.ennejb.cn{url}'
            request_header, request_data, res_data = test_api(url=url, projects=projects,
                                                              environment=environment,
                                                              method=method, data=data, username=username,
                                                              password=password)


            create_time = time.strftime("%Y-%m-%d %H:%M", time.localtime())
            r = res_data[0]
            # r = getValue(r, category)  # 获取要断言的参数的值
            expression = str_to_list(category)  # 转换为列表
            r = expression_value(response=r, expression=expression)
            if type(r) == int or type(r) == float:
                r = str(r)
                if r == assertion:
                    state = '2'  # 一致，通过
                else:
                    state = '3'  # 不通过
            elif r == assertion:
                state = '2'  # 一致，通过

            elif assertion == 'None':
                if r is None:
                    state = '2'
                else:
                    state = '3'
            else:
                state = '3'  # 不通过
            # 保存测试记录
            task_record = TestRecord(
                case_id=id[0],
                case_name = case.name,
                task_id=task_id,
                state=state,
                run_id = run_num,
                request_header=str(request_header),
                request_data=str(request_data),
                res_data=str(res_data),
                create_time=create_time,
            )

            db.session.add(task_record)

        db.session.commit()

    case_sum = TestRecord.query.filter_by(task_id=task_id,run_id=run_num).count()
    success_sum = TestRecord.query.filter_by(task_id=task_id, state=2, run_id=run_num).count()
    fail_sum = TestRecord.query.filter_by(task_id=task_id, state=3, run_id=run_num).count()
    skip_test = TestRecord.query.filter_by(task_id=task_id, state=1, run_id=run_num).count()
    id = task_id
    task = TestTask.query.get_or_404(id)

    create_time = time.strftime("%Y-%m-%d %H:%M", time.localtime())
    report = Report(
        report_name=task.task_name,
        task_id=task_id,
        run_id = run_num,
        # 1、全部通过 2、部分通过 3
        report_status=1,
        case_count=case_sum,
        test_success=success_sum,
        test_fail=fail_sum,
        skip_test=skip_test,
        create_name=task.create_name,
        create_time=create_time
    )

    db.session.add(report)

    db.session.commit()
    task.run_time = create_time
    task.task_status = 2
    logging.info('增加完成')
    db.session.commit()
    flash('运行完成,进入报告管理页查看报告')
    return redirect(url_for('test_task.task_manage'))


@test_task_bp.route('/delete/<task_id>', methods=['GET'])
def delete(task_id):
    task_id = TestTask.query.get_or_404(task_id)
    db.session.delete(task_id)
    db.session.commit()
    flash('操作成功')
    return redirect(url_for('test_task.task_manage' ))

@test_task_bp.route('/edit/<task_id>', methods=['GET','post'])
def edit(task_id):
    task = TestTask.query.get_or_404(task_id)
    if request.method == 'POST':
        task.task_type = request.form['task_type'],
        task.task_name = request.form['task_name'],
        task.run_environment = request.form['run_environment'],
        task.projects = ','.join(request.form.getlist('projects')),
        task.timing_configuration = request.form['timing_configuration'],
        task.accept_mail = request.form['accept_mail']
        db.session.commit()
        return jsonify({"message": "已修改"})
    projects = task.projects.split(',')

    return render_template('test/edit_task.html', task=task, projects=projects)


@test_task_bp.route('/log/<int:id>', methods=['GET'])
def log(id):
    record = TestRecord.query.filter_by(id=id).first()
    return render_template('test/log.html', header=record.request_header, body=record.request_data,
                           data=record.res_data, name=record.case_name,
                         time=record.create_time)