# 接口测试
import requests
import json
from urllib import parse
from applications.view.test.utils.function import getValue


# 获取登录凭证
class GetToken:
    def __init__(self,username,password,environment=None):
        self.username =username
        self.password = password
        self.environment = environment

    # 返回登录凭证
    def get_agent_token(self):
        headers = {'Content-Type': 'application/json;charset=UTF-8'}
        data = {
            "userName": self.username,
            "password": self.password,
        }
        if self.environment == '测试':
            url = 'https://api_test.com/login'
        else:
            url = 'https://api.com/login'
        try:
            r = requests.post(url=url, headers=headers, data=json.dumps(data)).json()
            agent_token = getValue(r, "data.agentToken")
        except KeyError:
            print('参数错误,不能获取token')
        return agent_token


# 测试接口
def test_api(projects,environment, url, method, data,username=None,password=None, story=None):
    method = method.upper()
    if environment == "测试":
        header = {
            'Content-Type': 'application/json;charset=UTF-8',
        }

    else:
        header = {
            'Content-Type': 'application/json;charset=UTF-8',
        }

    if method == 'GET':
        try:
            r = requests.get(url, headers=header).json()
        except ValueError:
            raise '登录后再试'
        request_header = []
        request_header.append(header)
        request_data= []
        request_data.append(data)
        res_data = []
        try:
            res_data.append(r)
        except ValueError:
            raise f'参数错误,不能获取token。{header}'
        return request_header,request_data,res_data

    elif method == 'POST':

        if story:
            data = json.dumps(data)
        else:
            data = data.encode('utf-8')
        try:
            r = requests.post(url, headers=header, data=data).json()
            print(r)
            request_header = []
            request_header.append(header)
            request_data = []
            request_data.append(data)
            res_data = []
            res_data.append(r)
            return request_header, request_data, res_data
        except Exception:
            r = requests.post(url, headers=header, data=data)
            r = r.text
            request_header = []
            request_header.append(header)
            request_data = []
            request_data.append(data)
            res_data = []
            res_data.append(r)
            print(request_header, request_data, res_data)
            return request_header, request_data, res_data

    elif method == 'PUT':

        r = requests.put(url, headers=header, data=data).json()
        request_header = []
        request_header.append(header)
        request_data= []
        request_data.append(data)
        res_data = []
        try:
            res_data.append(r)

        except ValueError:
            print(f'参数错误,不能获取token。{header}')
        return request_header,request_data,res_data

    elif method == 'PATCH':
        r = requests.patch(url, headers=header, data=data).json()
        request_header = []
        request_header.append(header)
        request_data= []
        request_data.append(data)
        res_data = []
        try:
            res_data.append(r)
        except ValueError:
            print(f'参数错误,不能获取token。{header}')
        return request_header,request_data,res_data

    else:
        r = requests.delete(url, headers=header, data=data).json()
        request_header = []
        request_header.append(header)
        request_data= []
        request_data.append(data)
        res_data = []
        try:
            res_data.append(r)
        except ValueError:
            print(f'参数错误,不能获取token。{header}')
        return request_header,request_data,res_data