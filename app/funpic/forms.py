from flask_wtf import FlaskForm
from wtforms import SubmitField


class Funpic(FlaskForm):
    submit = SubmitField('Refresh [Admin]')
