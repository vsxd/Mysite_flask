from flask import render_template, abort, redirect, request, url_for, flash, send_from_directory
from ..models import FunPic
from flask_login import login_required, current_user
from . import funpic
from .. import db
from .forms import Funpic
from ..decorators import admin_required


@funpic.route('/disable/<id>')
@login_required
@admin_required
def download_disable(id):
    file = FunPic.query.get_or_404(id)
    file.disabled = True
    db.session.add(file)
    db.session.commit()
    return redirect(url_for('funpic.girls',
                            page=request.args.get('page', 1, type=int)))


@funpic.route('/enable/<id>')
@login_required
@admin_required
def download_enable(id):
    file = FunPic.query.get_or_404(id)
    file.disabled = False
    db.session.add(file)
    db.session.commit()
    return redirect(url_for('funpic.girls',
                            page=request.args.get('page', 1, type=int)))


@funpic.route('/girls')
def girls():
    form = Funpic()
    query = FunPic.query
    # if form.validate_on_submit():
    #     ls = LinkSaver()
    #     ls.save_to_database()
    #     redirect(url_for('.funpic'))
    pagination = query.order_by(FunPic.timestamp.desc()).paginate(per_page=5)
    links = pagination.items
    return render_template('funpic/funpic.html',
                           form=form,
                           links=links,
                           girls=True,
                           pagination=pagination)


@funpic.route('/funny')
def funny():
    query = FunPic.query
    pagination = query.order_by(FunPic.timestamp.desc()).paginate(per_page=5)
    links = pagination.items
    return render_template('funpic/funpic.html',
                           links=links,
                           girls=False,
                           pagination=pagination)


# @funpic.route('/', methods=['GET', 'POST'])
# # 暂时不要求注册帐号才能访问 @login_required
# def updown():
#     form = UploadForm()
#     if form.validate_on_submit():
#         if not request.files['file']:
#             flash('上传失败 请重试', category='error')
#             return redirect(url_for('.updown'))
#         file = request.files['file']  # 直接从request对象中获取file
#         filename = secure_filename(file.filename)
#         extension = os.path.splitext(filename)[1][1:]  # 取扩展名并丢掉'.'
#         if not form.hashname.false_values:
#             filename = Updown.filename_hash(filename)
#         upload = Updown(filename=filename,
#                         extension=extension,
#                         uploader=current_user.id,
#                         note=form.note.data)
#         try:
#             file.save('app/static/download/' + file.filename)
#             # request对象中的file对象的save方法同样从项目根目录开始寻找目录
#             flash('上传成功', category='message')
#             db.session.add(upload)
#             db.session.commit()
#         except Exception as e:
#             flash('上传失败', category='error')
#         return redirect(url_for('.updown'))
#     query = Updown.query
#     # 显示服务器上的文件
#     pagination = query.order_by(Updown.timestamp.desc()).paginate(per_page=20)
#     files = pagination.items
#     return render_template('updown/updown.html',
#                            upform=form,
#                            files=files,
#                            pagination=pagination)
