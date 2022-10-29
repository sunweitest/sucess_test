import re
import time
# 使用方法，获得接口返回的数据，调用这个函数。
# r = requests.request()
# getValue.(r,code)


def getValue(date, keys, default=None):
    # default=None，在key值不存在的情况下，返回None
    keys_list = keys.split('.')
    # 以“.”为间隔，将字符串分裂为多个字符串，其实字符串为字典的键，保存在列表keys_list里
    if isinstance(date,dict):
        # 如果传入的数据为字典
        dictionary = dict(date)
        # 初始化字典
        for i in keys_list:
            # 按照keys_list顺序循环键值
            try:
                if dictionary.get(i) != None:
                    dict_values = dictionary.get(i)
                # 如果键对应的值不为空，返回对应的值
                elif dictionary.get(i) == None:
                    dict_values = dictionary.get(int(i))
                # 如果键对应的值为空，将字符串型的键转换为整数型，返回对应的值
            except:
                return default
                    # 如果字符串型的键转换整数型错误，返回None
            dictionary = dict_values
        return dictionary
    else:
        # 如果传入的数据为非字典
        try:
            dictionary = dict(eval(date))
            # 如果传入的字符串数据格式为字典格式，转字典类型，不然返回None
            if isinstance(dictionary,dict):
                for i in keys_list:
                    # 按照keys_list顺序循环键值
                    try:
                        if dictionary.get(i) != None:
                            dict_values = dictionary.get(i)
                        # 如果键对应的值不为空，返回对应的值
                        elif dictionary.get(i) == None:
                            dict_values = dictionary.get(int(i))
                        # 如果键对应的值为空，将字符串型的键转换为整数型，返回对应的值
                    except:
                        return default
                            # 如果字符串型的键转换整数型错误，返回None
                    dictionary = dict_values
                return dictionary
        except Exception:
            return default



# 替换url,data中的参数化变量{var}
def substitution_variable(var_dict=None, url=None, data=None):
    # var_dict = {"internetBarId": 10037, "startTime": '2022-01-28'}
    # url = '/bill?startTime={startTime}&endTime=2022-02-28&internetBarId={internetBarId}'
    if url:
        str_pat = re.compile(r'{(.*?)}')
        key_list = str_pat.findall(url)
        # print(key_list)

        if '{' in url:
            for i in key_list:
                if i == 'timestamp':

                    millis = int(round(time.time() * 1000)+1000)
                    var = millis
                    patter_str = '{%s}' % (i)
                    text = re.sub(pattern=patter_str, repl=f'{var}', string=url)
                    url = text
                    return url
                else:
                    var = var_dict.get(f'{i}')
                    patter_str = '{%s}' % (i)
                    text = re.sub(pattern=patter_str, repl=f'{var}', string=url)
                    url = text
                    return url
        else:
            return url
    else:
        for k in data:


            # 如果value是int，跳过替换，继续循环查找下一个value
            if type(data[k]) == int:
                continue
            elif '{' in data[k]:
                # print(data[k])
                data[k] = var_dict[k]
            else:
                continue
        return data
# print(substitution_variable())


def expression_value(response, expression):
    expression_len = len(expression)
    k = 1
    for i in expression:
        globals()['v' + str(k)] = i
        k += 1
    if expression_len == 1:
        try:
            return response[v1]
        except Exception:
            pass
    if expression_len == 2:
        try:
            return response[v1][v2]
        except Exception:
            pass

    if expression_len == 3:

        return response[v1][v2][v3]

    if expression_len == 4:
        return response[v1][v2][v3][v4]

    if expression_len == 5:
        return response[v1][v2][v3][v4][v5]
# response = {"status":200,"msg":None,"data":{'totalItems': 2, 'list': [{'internetBarId': 10037}]}}
# expression = ['data', 'list', 0, 'internetBarId']
# print(expression_value(response, expression ))
# r = response['data']['list'][0]['internetBarId']
# print(r)
# print(len(expression))

def str_to_list(string):
    expression = [ i for i in string.split(',') ]
    j = 0

    for i in expression:
        try:
            expression[j] = int(expression[j])
        except Exception:
            pass
        j += 1

    return expression

# k = 0
# for i in expression:
#     k += 1
#     locals()['v'+str(k)] = i
# if len(expression) == 3:
#     print(v1, v2, v3)
#     print(response[v1][v2][v3])
# print(locals())


# def expression_value_1(response: str, expression):
#     expression_len = len(expression)
#     globals()['v1'] = expression[1]
#     globals()['v2'] = expression[1]
#     globals()['v2'] = expression[1]
    # v1 = expression[1]
    # v2 = expression[2]
    # return response['v1'][v1][v2]


# print(expression_value_1(response=response, expression=expression))
# def test():
#     globals()['a2'] = 9
# test()
# print(a2)
# print(expression[2])


# var_dict = {"userName": "dailishang19", "contactUser": '代理商19'}

# userName = "dailishang12"
# data  = '{"userName": "{userName}","companyName":"合肥马到成功代理商有限公司","contactUser":"代理商12","tel":"13173616899"}'
# # print(data)
# data = eval(data)
# dict_value = data.values()
# dict_value_list = str(list(dict_value)) # 获取字典值，转换为列表
#
# print(dict_value_list)
# for k in data:
#     if '{' in data[k]:
#         print(data[k])
#         data[k] = var_dict[k]
#         print(data[k])
# print(data)
