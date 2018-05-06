from flask import jsonify, request, url_for, current_app
from ..models import Updown
from . import api


@api.route('/updown/list')
def get_list():
    page = request.args.get('page', 1, type=int)
    query = Updown.query
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
