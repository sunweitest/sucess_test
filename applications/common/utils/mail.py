from flask_mail import Message

from applications.extensions.init_mail import mail

recipients = {"test":""}
# send_mail(subject='title', recipients=['123@qq.com'], content='body')
def send_mail(subject, recipients, create_name, url, case_id, data, old_data):
    try:
        content = f''' 接口地址：{url}，用例id：{case_id}，新报文：{data}，报文：{old_data}'''

        message = Message(subject=subject, recipients=recipients, body=content)
        mail.send(message)
    except Exception as e:

        print('邮箱发送出错了')
        raise