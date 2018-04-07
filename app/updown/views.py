from flask import render_template, abort, redirect, request, url_for, flash, send_from_directory
from ..models import Updown
from flask_login import login_required, current_user
from .forms import UploadForm
from . import updown
from .. import db
import os
from werkzeug.utils import secure_filename
from ..decorators import admin_required


@updown.route('/disable/<id>')
@login_required
@admin_required
def download_disable(id):
    file = Updown.query.get_or_404(id)
    file.disabled = True
    db.session.add(file)
    db.session.commit()
    return redirect(url_for('updown.updown',
                            page=request.args.get('page', 1, type=int)))


@updown.route('/enable/<id>')
@login_required
@admin_required
def download_enable(id):
    file = Updown.query.get_or_404(id)
    file.disabled = False
    db.session.add(file)
    db.session.commit()
    return redirect(url_for('updown.updown',
                            page=request.args.get('page', 1, type=int)))


@updown.route('/download/<filename>')
def download(filename):
    if os.path.isfile(os.path.join('app/static/download/', filename)):
        # 此处有个坑 os.path是以项目根目录搜索
        # 而flask的send_from_directory方法是从app根目录开始搜索
        flash('开始下载：' + filename, category='info')
        return send_from_directory('static/download/', filename, as_attachment=True)
    else:
        flash('抱歉，文件没有在服务器上找到', category='error')
        return abort(404)


@updown.route('/', methods=['GET', 'POST'])
# 暂时不要求注册帐号才能访问 @login_required
def updown():
    form = UploadForm()
    if form.validate_on_submit():
        if not request.files['file']:
            flash('上传失败 请重试', category='error')
            return redirect(url_for('.updown'))
        file = request.files['file']  # 直接从request对象中获取file
        filename = secure_filename(file.filename)
        extension = os.path.splitext(filename)[1][1:]  # 取扩展名并丢掉'.'
        filename = os.path.splitext(filename)[0]  # 取文件名
        if form.hashname.data:
            filename = Updown.filename_hash(filename)
        upload = Updown(filename=filename,
                        extension=extension,
                        uploader=current_user.id,
                        note=form.note.data)
        try:
            file.save('app/static/download/' + filename + '.' + extension)
            # request对象中的file对象的save方法同样从项目根目录开始寻找目录
            flash('上传成功', category='message')
            db.session.add(upload)
            db.session.commit()
        except Exception as e:
            flash('上传失败', category='error')
        return redirect(url_for('.updown'))
    query = Updown.query
    # 显示服务器上的文件
    pagination = query.order_by(Updown.timestamp.desc()).paginate(per_page=20)
    files = pagination.items
    return render_template('updown/updown.html',
                           upform=form,
                           files=files,
                           pagination=pagination)
