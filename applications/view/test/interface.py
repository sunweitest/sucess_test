from flask import render_template, request, url_for, redirect, Blueprint, flash, jsonify
from applications.models import Api, ApiHistory
from applications.common.utils.rights import authorize



interface_bp = Blueprint('interface', __name__, url_prefix='/interface')


@interface_bp.route('/', defaults={'page': 1})
@interface_bp.route('/page/<int:page>')
@authorize("interface:manage:main", log=True)
def interface(page):
    per_page = 16
    pagination = Api.query.order_by(-Api.id).paginate(page, per_page=per_page)  # 分页对象
    api = pagination.items  # 当前页数的记录列表
    return render_template('test/interface.html', pagination=pagination, api=api)

@interface_bp.get('/edit/<int:id>')
def edit(id):
    return render_template('test/interface/edit.html')