from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length


class Register(FlaskForm):
    username = StringField(label='username',
                           validators=[DataRequired()],
                           render_kw={
                               'placeholder': 'username',
                               'class': 'input_test'
                           })
    password = PasswordField(label='password',
                             validators=[DataRequired(),
                                         Length(3, 8, '密码长度必须在3-8之间')])

    cpassword = PasswordField(label='cpassword',validators=[DataRequired(),
                                                            EqualTo('password', '两次密码不一致')])
    submit = SubmitField('提交')


class Add(FlaskForm):
    name = StringField(label='名称', validators=[DataRequired()])
    project = StringField(label='项目', validators=[DataRequired()])
    var_dict = TextAreaField(label='故事变量字典')
    submit = SubmitField('提交')


class AddScene(Add):
    before = StringField(label='前置', validators=[DataRequired()])
    after = StringField(label='后置')
    case_list = StringField(label='用例列表')
    category = StringField(label='获取响应值', validators=[DataRequired()])
    assertion = StringField(label='验证', validators=[DataRequired()])
    comment = TextAreaField(label='笔记')
    submit = SubmitField('提交')


class Story(Add):
    rms_username = StringField(label='用户名')
    rms_password = StringField(label='密码')
    password = StringField(label='密码')
    submit = SubmitField('提交')