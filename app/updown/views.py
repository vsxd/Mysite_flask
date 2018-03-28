from flask import render_template, redirect, request, url_for, flash
from ..models import Updown
from flask_login import login_required, current_user
from .forms import UploadForm
from . import updown
from .. import db
from os import path
from werkzeug.utils import secure_filename


@updown.route('/', methods=['GET', 'POST'])
# @login_required
def updown():
    form = UploadForm()

    if form.validate_on_submit():
        if not request.files['file']:
            flash('上传失败 请重试')
            return redirect(url_for('.updown'))
        file = request.files['file']  # 直接从request对象中获取file
        filename = secure_filename(file.filename)
        extension = path.splitext(filename)[1][1:]  # 取扩展名并丢掉'.'
        if not form.hashname.false_values:
            filename = Updown.filename_hash(filename)
        upload = Updown(filename=filename,
                        extension=extension,
                        uploader=current_user.id,
                        note=form.note.data)
        db.session.add(upload)
        db.session.commit()
        file.save('updown/' + file.filename)
        flash('上传成功')
        return redirect(url_for('.updown'))
    query = Updown.query
    # 显示服务器上的文件
    pagination = query.paginate(per_page=20)
    files = pagination.items
    return render_template('updown/updown.html',
                           upform=form,
                           files=files,
                           pagination=pagination)
