import os

from flask import jsonify, request, url_for, current_app, send_from_directory, abort

from app.api_v1.errors import bad_request
from ..models import Updown
from . import api_v1


@api_v1.route('/updown/list')
def get_list():
    page = request.args.get('page', 1, type=int)
    query = Updown.query.filter(Updown.disabled == False)
    # 显示服务器上的文件
    pagination = query.order_by(Updown.timestamp.desc()).paginate(per_page=20)
    files = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api_v1.get_posts', page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api_v1.get_posts', page=page+1)
    return jsonify({
        'file': [file.to_json() for file in files],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api_v1.route('/download/<filename>')
def download(filename):
    if os.path.isfile(os.path.join('app/updown/download/', filename)):
        # 此处有个坑 os.path是以项目根目录搜索
        # 而flask的send_from_directory方法是从app根目录开始搜索
        return send_from_directory('updown/download/', filename, as_attachment=True)
    else:
        return abort(404)
