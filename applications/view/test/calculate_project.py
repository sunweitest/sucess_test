from scipy import stats
from flask import render_template, request, url_for, redirect, Blueprint, flash, jsonify


project = Blueprint('project', __name__, url_prefix='/project')


@project.route('/')
def index():
    return render_template('test/calculate_project.html')


@project.route('/calculate/', methods=['get'])
def calculate_project():
    word = request.args.get('word')
    count_word = [1900, 2300, 2900, 2317]
    project_day = [7, 8, 10, 8]
    slope, intercept, r, p, std_err = stats.linregress(count_word, project_day)

    def model(a):

        return slope * a + intercept

    mymodel = list(map(model, count_word))
    # print('拟合度：', round(r, 3))
    day = model(int(word))
    day = round(day, 1)
    return jsonify({"code": 200, "message": f"从开发到测试完成，工期需要{day}天"})
