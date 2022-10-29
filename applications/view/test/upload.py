from flask import request, url_for, redirect, flash, Blueprint, send_from_directory
from applications.models import Case
from applications.extensions import db
import time
from werkzeug.utils import secure_filename
import xlrd
import os.path as op
import os

files_bp = Blueprint('files', __name__, url_prefix='/files')


@files_bp.route('/upload', methods=['get', 'post'])
def upload():
    if request.method == 'POST':
        f = request.files['file']
        try:
            upload_path = op.join('upload/')
        except Exception:
            os.makedirs('upload')
            upload_path = op.join('upload/')
        file_name = upload_path + secure_filename(f.filename)
        f.save(file_name)
        print('file uploaded successfully')
        data = xlrd.open_workbook(file_name)
        sheet1 = data.sheets()[0]
        sheet1_rows = sheet1.nrows

        for i in range(sheet1_rows):
            a = sheet1.row_values(i)
            if a[0] == '环境':
                continue
            environment = a[0]
            projects = a[1]
            name = a[2].replace('\n', '')
            module = a[3]
            url = a[4].replace('\t', '').replace('\n', '')
            method = a[5]
            data = a[6]
            category = a[8]
            assertion = a[9]
            username = a[7]
            password = a[10]





            create_name = a[11]
            case = Case(
                name=name,
                url=url,
                method=method,
                data=data,
                environment=environment,
                module=module,
                headers='',
                category=category,
                assertion=assertion,
                state=1,
                username=username or None,
                password=password or None,
                datetime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                projects=projects,
                test_time=None,
                create_name=create_name,
                after=''
            )

            db.session.add(case)
        db.session.commit()
    flash('批量添加成功')
    return redirect(url_for('smart_test.apitest'))


@files_bp.route('/download', methods=['get', 'post'])
def download():

    directory = os.getcwd()  # 当前目录
    filename = 'temp.xls'
    return send_from_directory(directory, filename, as_attachment=True)