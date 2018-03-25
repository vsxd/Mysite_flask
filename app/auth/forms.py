from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('保持登录状态')
    submit = SubmitField('登录')


class RegistrationForm(FlaskForm):
    email = StringField('密码', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    username = StringField('昵称', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               '昵称只能包含 字母, 数字, 点 或者 下划线')])
    password = PasswordField('密码', validators=[
        DataRequired(), EqualTo('password2', message='密码必须一致')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('注册帐号')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('此Email已经被注册过')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('昵称已经被使用')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('旧密码', validators=[DataRequired()])
    password = PasswordField('新密码', validators=[
        DataRequired(), EqualTo('password2', message='密码必须一致')])
    password2 = PasswordField('确认密码',
                              validators=[DataRequired()])
    submit = SubmitField('更新账户密码')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    submit = SubmitField('重新设置密码')


class PasswordResetForm(FlaskForm):
    password = PasswordField('新密码', validators=[
        DataRequired(), EqualTo('password2', message='两次密码必须一致')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('设置密码')


class ChangeEmailForm(FlaskForm):
    email = StringField('新Email地址', validators=[DataRequired(), Length(1, 64),
                                                 Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('更改Email地址')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('此Email已经被注册过')
