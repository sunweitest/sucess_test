import logging
import os
import re
import arrow
import sqlite3
from contextlib import closing
from os.path import join, exists
from werkzeug.utils import secure_filename
from .mind2testcase.zentao import xmind_to_zentao_csv_file
from .mind2testcase.testlink import xmind_to_testlink_xml_file
from .mind2testcase.utils import get_xmind_testsuites, get_xmind_testcase_list
from applications.common.utils.rights import authorize
from applications.common.utils.rights import authorize
from flask import Flask, request, send_from_directory, g, render_template, abort, redirect, url_for, Blueprint
from applications.extensions import db
from applications.models import Mind
from os import path as op

mind_bp = Blueprint('mind', __name__, url_prefix='/mind')

UPLOAD_FOLDER = op.join('upload/')
ALLOWED_EXTENSIONS = ['xmind']



def insert_record(xmind_name, note=''):
    now = str(arrow.now())
    mind = Mind(
        name=xmind_name,
        create_on=now,
        note=str(note),
        is_deleted=0
    )
    db.session.add(mind)
    db.session.commit()


def delete_record(filename, record_id):
    xmind_file = join(UPLOAD_FOLDER, filename)
    testlink_file = join(UPLOAD_FOLDER, filename[:-5] + 'xml')
    zentao_file = join(UPLOAD_FOLDER, filename[:-5] + 'csv')

    for f in [xmind_file, testlink_file, zentao_file]:
        if exists(f):
            os.remove(f)

    update = Mind.query.filter_by(id=record_id).update({"is_deleted": 1})
    db.session.commit()


def delete_records(keep=20):
    """Clean up files on server and mark the record as deleted"""
    sql = "SELECT * from mind where is_deleted != 1 ORDER BY id desc"
    cursor = db.session.execute(sql)

    rows = cursor.fetchall()
    for row in rows:
        name = row[1]
        xmind_file = join(UPLOAD_FOLDER, name)
        testlink_file = join(UPLOAD_FOLDER, name[:-5] + 'xml')
        zentao_file = join(UPLOAD_FOLDER, name[:-5] + 'csv')

        for f in [xmind_file, testlink_file, zentao_file]:
            if exists(f):
                os.remove(f)
    Mind.query.filter_by(id=row[0]).update({"is_deleted": 1})
    db.session.commit()


def get_latest_record():
    found = list(get_records(1))
    if found:
         return found[0]


def get_records(limit=8):
    short_name_length = 120


    rows = db.session.query(Mind).filter(Mind.is_deleted != 1).all()
    for row in rows:

        name, short_name, create_on, note, record_id = row.name, row.name, row.create_on, row.note, row.id
        # shorten the name for display
        if len(name) > short_name_length:
            short_name = name[:short_name_length] + '...'

        # more readable time format
        create_on = arrow.get(create_on).humanize()
        yield short_name, name, create_on, note, record_id


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def check_file_name(name):
    secured = secure_filename(name)
    if not secured:
        secured = re.sub('[^\w\d]+', '_', name)  # only keep letters and digits from file name
        assert secured, 'Unable to parse file name: {}!'.format(name)
    return secured + '.xmind'


def save_file(file):
    if file and allowed_file(file.filename):
        # filename = check_file_name(file.filename[:-6])
        filename = file.filename
        upload_to = join(UPLOAD_FOLDER, filename)

        if exists(upload_to):
            filename = '{}_{}.xmind'.format(filename[:-6], arrow.now().strftime('%Y%m%d_%H%M%S'))
            upload_to = join(UPLOAD_FOLDER, filename)

        file.save(upload_to)
        insert_record(filename)
        g.is_success = True
        return filename

    elif file.filename == '':
        g.is_success = False
        g.error = "Please select a file!"

    else:
        g.is_success = False
        g.invalid_files.append(file.filename)


def verify_uploaded_files(files):
    # download the xml directly if only 1 file uploaded
    if len(files) == 1 and getattr(g, 'is_success', False):
        g.download_xml = get_latest_record()[1]

    if g.invalid_files:
        g.error = "Invalid file: {}".format(','.join(g.invalid_files))


@mind_bp.route('/', methods=['GET', 'POST'])
@authorize("mind_bp:index:index", log=True)
def index(download_xml=None):
    g.invalid_files = []
    g.error = None
    g.download_xml = download_xml
    g.filename = None

    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        g.filename = save_file(file)
        verify_uploaded_files([file])
        # delete_records()

    else:
        g.upload_form = True

    if g.filename:
        return redirect(url_for('mind.preview_file', filename=g.filename))
    else:
        return render_template('mind/index.html', records=list(get_records()))


@mind_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@mind_bp.route('/<filename>/to/testlink')
def download_testlink_file(filename):
    full_path = join(UPLOAD_FOLDER, filename)
    if not exists(full_path):
        abort(404)

    testlink_xmls_file = xmind_to_testlink_xml_file(full_path)
    filename = os.path.basename(testlink_xmls_file) if testlink_xmls_file else abort(404)

    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)


@mind_bp.route('/<filename>/to/zentao')
def download_zentao_file(filename):
    full_path = join(UPLOAD_FOLDER, filename)

    if not exists(full_path):
        abort(404)

    zentao_csv_file = xmind_to_zentao_csv_file(full_path)
    filename = os.path.basename(zentao_csv_file) if zentao_csv_file else abort(404)
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)


@mind_bp.route('/preview/<filename>')
def preview_file(filename):
    full_path = join(UPLOAD_FOLDER, filename)
    print(full_path)
    testsuites = get_xmind_testsuites(full_path)
    suite_count = 0
    for suite in testsuites:
        suite_count += len(suite.sub_suites)

    testcases = get_xmind_testcase_list(full_path)
    return render_template('mind/preview.html', name=filename, suite=testcases, suite_count=suite_count)


@mind_bp.route('/delete/<filename>/<int:record_id>')
def delete_file(filename, record_id):
    full_path = join(UPLOAD_FOLDER, filename)

    if not exists(full_path):
        abort(404)
    else:
        delete_record(filename, record_id)
    return redirect('/mind/')