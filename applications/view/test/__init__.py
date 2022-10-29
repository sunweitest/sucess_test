from applications.view.test.api_test import test_bp
from applications.view.test.test_task import test_task_bp
from applications.view.test.report import report_bp
from applications.view.test.batch import batch_test_bp
from applications.view.test.upload import files_bp
from applications.view.test.story import story
from applications.view.test.calculate_project import project
from . import api_test, test_task, report, upload, batch
from applications.view.test.interface import interface_bp

def register_test_view(app):
    app.register_blueprint(test_bp)
    app.register_blueprint(test_task_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(batch_test_bp)
    app.register_blueprint(story)
    app.register_blueprint(files_bp)
    app.register_blueprint(project)
    app.register_blueprint(interface_bp)