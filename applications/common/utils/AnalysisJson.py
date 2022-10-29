import os, requests
from loguru import logger
from applications.common.utils.processingJson import write_data, get_json_
from applications.common.utils.mail import send_mail
from applications.models import Api, ApiHistory, Case
from applications.extensions import db
import time
import pymysql
from dotenv import dotenv_values


HOST = '127.0.0.1'
PORT = 3306

DATABASE = 'TEST'
USERNAME = 'root'
PASSWORD = '123456'
db = pymysql.connect(host=HOST, port=int(PORT), user=USERNAME, password=PASSWORD, charset='utf8mb4')

# 获取接口文档的json文件，转换成字典，再保存到数据库
class AnalysisJson:
    def __init__(self, url):
        self.url = url
        self.interface = {}
        self.case_list = []
        self.tags_list = []
        self.http_suite = {"config": {"name": "", "base_url": "", "variables": {}},
                           "testcases": []}
        self.http_testcase = {"name": "", "testcase": "", "variables": {}}

        # api_all = db.session.query(Api.url).all()
        cursor = db.cursor()
        cursor.execute("select url from Test.api")
        api_all = cursor.fetchall()
        # api_all = Api.query.all()
        # self.api_url_list = [i.url for i in api_all]
        self.api_url_list = []
        for api in api_all:
            self.api_url_list.append(api[0])

    def retrieve_data(self):
        """主函数:return:"""
        try:
            r = requests.get(self.url).json()
            write_data(r, 'data.json')
            # r = get_json('D:\HttpRunner_framework\\testcases\data.json')
        except Exception as e:
            logger.error('请求swagger url 发生错误. 详情原因: {}'.format(e))
            return 'error'
        self.data = r['paths']  # 接口数据
        self.url = 'https://' + r['host']
        self.title = r['info']['title']
        self.http_suite['config']['name'] = self.title

        self.http_suite['config']['base_url'] = self.url
        self.definitions = r['definitions']  # body参数
        for tag_dict in r['tags']:
            self.tags_list.append(tag_dict['name'])
        i = 0
        for tag in self.tags_list:
            self.http_suite['testcases'].append({"name": "", "testcase": "", "variables": {}})
            self.http_suite['testcases'][i]['name'] = tag
            self.http_suite['testcases'][i]['testcase'] = 'testcases/' + tag + '.json'
            i += 1

        suite_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname("__file__"), os.path.pardir)))
        testcase_path = os.path.join(suite_path, 'demo_testsuite.json')

        write_data(self.http_suite, testcase_path)
        if isinstance(self.data, dict):
            for tag in self.tags_list:
                self.http_case = {"config": {"name": "", "base_url": "", "variables": {}}, "teststeps": []}
                for key, value in self.data.items():
                    for method in list(value.keys()):
                        params = value[method]

                        # print(params)
                        # if not params['deprecated']:  # 接口是否被弃用
                        if params['tags'][0] == tag:
                            self.http_case['config']['name'] = params['tags'][0]
                            self.http_case['config']['base_url'] = self.url
                            case = self.retrieve_params(params, key, method, tag)

                            print("循环")
                            self.http_case['teststeps'].append(case)
                        else:
                            logger.info(
                                'interface path: {}, if name: {}, is deprecated.'.format(key, params['description']))
                            break
                api_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname("__file__"), os.path.pardir)),
                                        'testcases')
                testcase_path = os.path.join(api_path, tag + '.json')
                write_data(self.http_case, testcase_path)

        else:
            logger.error('解析接口数据异常！url 返回值 paths 中不是字典.')
            return 'error'
        db.close()
    def retrieve_params(self, params, api, method, tag):
        """
        解析json，把每个接口数据都加入到一个字典中
        :param params:
        :param params_key:
        :param method:
        :param key:
        :return:
        replace('false', 'False').replace('true', 'True').replace('null','None')
        """
        http_interface = {"name": "", "variables": {},
                          "request": {"url": "", "method": "", "headers": {}, "json": {}, "params": {}}, "validate": [],
                          "output": []}
        http_testcase = {"name": "", "api": "", "variables": {}, "validate": [], "extract": [], "output": []}

        name = params['summary'].replace('/', '_')
        http_interface['name'] = name
        http_testcase['name'] = name
        http_testcase['api'] = 'api/{}/{}.json'.format(tag, name)
        http_interface['request']['method'] = method.upper()
        http_interface['request']['url'] = api.replace('{', '$').replace('}', '')
        parameters = params.get('parameters')  # 未解析的参数字典
        responses = params.get('responses')
        if not parameters:  # 确保参数字典存在
            parameters = {}
        for each in parameters:
            if each.get('in') == 'body':  # body 和 query 不会同时出现
                schema = each.get('schema')
                if schema:
                    ref = schema.get('$ref')
                    if ref:
                        param_key = ref.split('/')[-1]
                        param = self.definitions[param_key]['properties']
                        for key, value in param.items():
                            if 'example' in value.keys():
                                http_interface['request']['json'].update({key: value['example']})
                            else:
                                http_interface['request']['json'].update({key: ''})

            elif each.get('in') == 'query':
                name = each.get('name')
                for key in each.keys():
                    if 'example' in key:
                        http_interface['request']['params'].update({name: each[key]})
        for each in parameters:
            # if each.get('in') == 'path':
            #     name = each.get('name')
            #     for key in each.keys():
            #         if 'example' in key:
            #             http_interface['request']['json'].update({name: each[key]})
            #     else:
            #
            #         http_interface['request']['json'].update({name: ''})
            if each.get('in') == 'header':
                name = each.get('name')
                for key in each.keys():
                    if 'example' in key:
                        http_interface['request']['headers'].update({name: each[key]})
                    else:
                        if name == 'token':
                            http_interface['request']['headers'].update({name: '$token'})
                        else:
                            http_interface['request']['headers'].update({name: ''})
        for key, value in responses.items():
            schema = value.get('schema')
            if schema:
                ref = schema.get('$ref')
                if ref:
                    param_key = ref.split('/')[-1]
                    res = self.definitions[param_key]['properties']
                    i = 0

                    for k, v in res.items():
                        if 'example' in v.keys():
                            http_interface['validate'].append({"eq": []})
                            http_interface['validate'][i]['eq'].append('content.' + k)
                            http_interface['validate'][i]['eq'].append(v['example'])

                            http_testcase['validate'].append({"eq": []})
                            http_testcase['validate'][i]['eq'].append('content.' + k)
                            http_testcase['validate'][i]['eq'].append(v['example'])
                            i += 1
                else:
                    http_interface['validate'].append({"eq": []})
            else:
                http_interface['validate'].append({"eq": []})
        if http_interface['request']['json'] == {}:
            del http_interface['request']['json']
        if http_interface['request']['params'] == {}:
            del http_interface['request']['params']
        # 每条url解析后，做处理
        url = http_interface['request']['url']
        # 如果接口存在，检查参数是否改变。
        cursor = db.cursor()
        print(self.api_url_list)

        if url in self.api_url_list:
            try:
                data = http_interface['request']['json']
                cursor.execute("select * from Test.api where url=%s", url)
                api = cursor.fetchone()
                old_data = api[4]
                # old_data = dict(raw_old_data)
                # print(data,type(data),old_data,type(data))
                # print(data == old_data)
                if data == old_data:
                    print("data相等")
                else:
                    # 更新api的参数
                    # api_url.data = data
                    update_time = time.strftime("%Y-%m-%d %H:%M", time.localtime())
                    data = str(data)
                    url = str(url)
                    update_sql = "UPDATE Test.api SET data = %s, updata_time = %s where url= %s"
                    cursor.execute(update_sql, (data, update_time,url))


                    db.commit()
                    # api_case = Case.query.filter_by(url=url).all()
                    cursor.execute("select * from Test.case where url=%s", url)
                    api_case = cursor.fetchall()
                    # db.session.commit()

                    for case in api_case:
                        create_name = case[17]
                        case_id = case[0]
                        # recipients = ['sunweiyouxiang@hotmail.com']
                        # send_mail(subject="接口有变化", recipients=['sunweiyouxiang@hotmail.com'],
                        #            create_name=create_name, url=url, case_id=case.id, data=data, old_data=old_data)
                        robot_url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=862a520c-fd1c-4eb3-b9ae-8150d330f9d1'
                        robot_header = {'Content-Type': 'application/json; charset=UTF-8'}
                        content = f''' 接口地址：{url}，用例id：{case_id}，用例创建：{create_name}，新报文：{data}，原报文：{old_data}'''
                        robot_body = {
                            "msgtype": "text",
                            "text": {
                                "content": content,
                                "mentioned_list": [create_name]
                            }
                        }
                        response = requests.post(url=robot_url, json=robot_body, headers=robot_header)
                        print(f"接口更新完成已发送{response}")

            except KeyError:
                print("get")
            # api_url = Api.query.filter_by(url=url).first()

        else:
            # 保存到数据库
            try:
                sql = "INSERT INTO `Test`.`api` (`name`, `url`, `headers`, `data`,`method`,`create_time`) VALUES (%s,%s,%s,%s,%s,%s)"
                _time = time.strftime("%Y-%m-%d %H:%M", time.localtime())
                name = http_interface['name']
                name = str(name)
                header = http_interface['request']['headers']
                header = str(header)
                _json = http_interface['request']['json']
                data = str(_json)
                method = http_interface['request']['method']
                method = str(method)
                cursor.execute(sql, (name, url, header, data, method, _time))
            except KeyError:
                sql = "INSERT INTO `Test`.`api` (`name`, `url`, `headers`,`method`,`create_time`) VALUES (%s,%s,%s,%s,%s)"
                _time = time.strftime("%Y-%m-%d %H:%M", time.localtime())
                name = http_interface['name']
                name = str(name)
                header = http_interface['request']['headers']
                header = str(header)
                method = http_interface['request']['method']
                method = str(method)
                cursor.execute(sql, (name, url, header,method, _time))

            # db.session.add(api)
            db.commit()
        api_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname("__file__"), os.path.pardir)), 'api')
        tags_path = os.path.join(api_path, tag)
        if not os.path.exists(tags_path):

            os.mkdir(tags_path)
        json_path = os.path.join(tags_path, http_interface['name'] + '.json')
        write_data(http_interface, json_path)
        return http_testcase


if __name__ == '__main__':
    AnalysisJson('https://petstore.swagger.io/v2/swagger.json').retrieve_data()