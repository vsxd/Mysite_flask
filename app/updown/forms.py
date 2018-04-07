from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length
# from wtforms import ValidationError


class UploadForm(FlaskForm):
    file = FileField('上传文件', validators=[FileRequired('文件未选择！'),
                                         FileAllowed(['jpg', 'png', 'torrent', 'txt'],
                                                     '只允许上传jpg png torrent以及txt文件')])
    note = StringField('文件说明', validators=[DataRequired(), Length(2, 64,
                                           message='请认真填写文件说明，但不能超过64个字符')])
    hashname = BooleanField('上传时随机文件名（选择此项后请认真填写文件说明）')
    submit = SubmitField('确认上传')

    def validate_file(self, field):
        # 验证文件大小? 验证文件名长度? 验证文件名是否重复?
        pass
