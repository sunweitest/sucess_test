from flask import render_template, request, url_for, redirect, flash, Blueprint
from applications.view.test.utils.apitest import test_api
from applications.view.test.utils.function import getValue
import urllib.parse
from applications.models import Case
from applications.extensions import db
import time
from os import path as op
from os import makedirs
from werkzeug.utils import secure_filename
import xlrd
from applications.common.utils.rights import authorize

batch_test_bp = Blueprint('batch_test_bp', __name__, url_prefix='/batch')


@batch_test_bp.route('/batch_test', methods=['GET', 'POST'])
def batch_test():
    caseid = request.args.get('caseid')
    caseid = urllib.parse.unquote(str(caseid))
    if caseid == "全部":
        id = db.session.query(Case.id).all()
        for id in id:
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
            module = case.module
            if environment == '测试':
                url = f'https://api_test/com{url}'

            else:
                url = f'https://api.com{url}'

            try:
                request_header, request_data, res_data = test_api(url=url, projects=projects, environment=environment,
                                                                  method=method, data=data, username=username,
                                                                  password=password)
            except Exception:
                continue
            case.test_time = time.strftime("%Y-%m-%d %H:%M", time.localtime())
            r = res_data[0]
            r = getValue(r, category)  # 获取要断言的参数的值
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


@batch_test_bp.route('/batch_add', methods=['get', 'post'])
@authorize("batch_test_bp:batch_add:main", log=True)
def batch_add():
    if request.method == 'POST':
        f = request.files['file']
        try:
            upload_path = op.join('upload/')
        except Exception:
            makedirs('upload')
            upload_path = op.join('upload/')

        file_name = upload_path + secure_filename(f.filename)
        f.save(file_name)
        print('file uploaded successfully')

        data = xlrd.open_workbook(file_name)
        sheet1 = data.sheets()[0]
        sheet1_rows = sheet1.nrows

        for i in range(sheet1_rows):
            a = sheet1.row_values(i)
            if a[0] == '接口名称':
                continue
            name = a[0].replace('\n', '')
            url = a[1].replace('\t', '').replace('\n', '')
            method = a[2]
            data = a[3]
            category = a[7]
            assertion = a[8]

            projects = a[5]
            module = a[6]

            case = Case(
                name=name,
                url=url,
                method=method,
                data=data,
                environment='测试',
                module=module,
                headers='',
                category=category,
                assertion=assertion,
                state=1,
                datetime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                projects=projects,
                test_time=None,
                create_name='yapi自动导入',
                # before=before,
                after=''
            )
            db.session.add(case)
        db.session.commit()

        flash('批量添加成功')
        return redirect(url_for('smart_test.apitest'))
    return render_template('test/batch_add_case.html')