import datetime
from applications.common.utils.AnalysisJson import AnalysisJson
task_list = ['TEST', 'task']



def TEST(a, b):
    # print(f'定时任务_1_{a},{b},{datetime.datetime.now()}')
    print("同步接口任务开始")
    AnalysisJson('https://petstore.swagger.io/v2/swagger.json').retrieve_data()
    print("完成")



def task(a, b):
    print(f'定时任务_5_{a}{b}{datetime.datetime.now()}')