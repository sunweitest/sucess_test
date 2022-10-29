from flask import render_template, Blueprint, redirect, url_for
from applications.common.utils.rights import authorize
from applications.models import TestTask, Report, TestRecord
from applications.extensions import db

report_bp = Blueprint('report', __name__, url_prefix='/report')


@report_bp.route('/<int:report_id>/<int:run_num>/', methods=['get'])
@authorize("report:report:main", log=True)
def test_report(report_id,run_num):
    report = Report.query.filter_by(id=report_id)

    # 查询任务id，拿任务id去测试记录表查询记录。
    task_id = db.session.query(Report.task_id).filter_by(id=report_id)


    test_record = TestRecord.query.filter_by(task_id=task_id,run_id=run_num).all()
    return render_template('test/test_report.html', report=report,record=test_record)


@report_bp.route('/report_manage', defaults={'page': 1})
@report_bp.route('/report_manage/page/<int:page>')
@authorize("report:report_manage:main", log=True)
def report_manage(page):
    per_page = 10
    pagination = Report.query.order_by(-Report.id).paginate(page, per_page=per_page)
    report = pagination.items
    return render_template('test/report_manage.html', pagination=pagination, report=report)


@report_bp.route('/delete/<report_id>', methods=['GET'])
def delete(report_id):
    report_id = Report.query.get_or_404(report_id)
    db.session.delete(report_id)
    db.session.commit()
    return redirect(url_for('report.report_manage'))