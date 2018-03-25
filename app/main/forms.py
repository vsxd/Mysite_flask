from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp
from wtforms import ValidationError
from flask_pagedown.fields import PageDownField
from ..models import Role, User


class NameForm(FlaskForm):
    name = StringField('你的名字是？', validators=[DataRequired()])
    submit = SubmitField('确认')


class EditProfileForm(FlaskForm):
    name = StringField('真实姓名', validators=[Length(0, 64)])
    location = StringField('位置', validators=[Length(0, 64)])
    about_me = TextAreaField('关于我')
    submit = SubmitField('确认')


class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    username = StringField('昵称', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               '昵称只能包含 字母, 数字, 点 或者 下划线')])
    confirmed = BooleanField('确认')
    role = SelectField('角色', coerce=int)
    name = StringField('真实姓名', validators=[Length(0, 64)])
    location = StringField('位置', validators=[Length(0, 64)])
    about_me = TextAreaField('关于我')
    submit = SubmitField('确认')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email已经被注册')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('昵称已经被使用')


class PostForm(FlaskForm):
    body = PageDownField('What\'s on your mind?', validators=[DataRequired()])
    submit = SubmitField('Post!')


class CommentForm(FlaskForm):
    body = StringField('输入您的评论', validators=[DataRequired()])
    submit = SubmitField('Comment！')
