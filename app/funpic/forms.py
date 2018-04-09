from flask_wtf import FlaskForm
from wtforms import SubmitField, BooleanField


class Funpic(FlaskForm):
    # rank = BooleanField('只显示评价高的图片')
    submit = SubmitField('Refresh [Admin]')
