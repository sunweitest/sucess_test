import re


def add_parameters(params, **kwargs):
    params.update(kwargs)


var_dict = {"internetBarId": 10037, "startTime": '2022-01-28'}

url = '/bill?startTime={startTime}&endTime=2022-02-28&internetBarId={internetBarId}'
str_pat = re.compile(r'{(.*?)}')
key_list = str_pat.findall(url)
print(key_list)

if '{' in url:
    for i in key_list:
        print(i)
        var = var_dict.get(f'{i}')
        # params = {}
        # add_parameters(params, i = var)
        # print(params)
        # url = url.format(i=var)

        #         url = url.format_map(vars(key_list))
        #         url.replace({internetBarId}, var)
        patter_str = '{%s}' % (i)
        text = re.sub(pattern=patter_str, repl=f'{var}', string=url)
        url = text
    print(url)

# if '{' in url:
#     var = var_dict.get(f'{i}')
#     url = url.format(=var)

#     url = url.format_map(vars(key_list))
#     print(url)
# import sys
#
#
# class safesub(dict):
#     def __missing__(self, key):
#         return '{' + key + '}'
#
#
# def sub(text):
#     return text.format_map(safesub(sys._getframe(1).f_locals))
#
#
# print(sub(url))
response = {"status":200,"msg":None,"data":[{"internetBarId":10037}]}
expression = ['data',0,'internetBarId']
expression_len = len(expression)
k = 0
for i in expression:
    k += 1
    name='v'+str(k)
    locals()['v'+str(k)] = i
print(v1, v2, v3)
# print(response.get(v1)[v2].get(v3))
print(response[v1][v2][v3])

import inspect


def test_list_pre():
    prepare_list = locals()
    for i in range(16):
        prepare_list['list_' + str(i)] = []
        prepare_list['list_' + str(i)].append(('第' + str(i) + '个list'))
    print(prepare_list['list_0'])
    print(prepare_list['list_1'])
    print(prepare_list['list_2'])


def get_variable_name(variable):
    callers_local_vars = inspect.currentframe().f_back.f_locals.items()
    return [var_name for var_name, var_val in callers_local_vars if var_val is variable]



# for i in range(2):
#     prepare_list['list_' + str(i)] = []
#     prepare_list['list_' + str(i)].append(('第' +str(i) + '个list'))
#     a = get_variable_name(prepare_list['list_0']).pop()
#
#     print(a) # 打印变量名

# test_list_pre()
# def sum_number(num):
#     print(num)
#     if num == 1:
#         return
#     sum_number(num -1 )
#
# sum_number(3)


def sum_numbers(num):
    if num == 1:
        return 1
    return num + sum_numbers(num -1 )
result = sum_numbers(3)
print(result )