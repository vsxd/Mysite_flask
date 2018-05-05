from flask import jsonify, request, g, url_for, current_app
from .. import db
from ..models import FunPic, Permission
from . import api
from .decorators import permission_required
from .errors import forbidden


@api.route('/funpic/funny')
def get_funny():
    page = request.args.get('page', 1, type=int)
    query = FunPic.query.filter_by(info='good').filter_by(type='funny')
    pagination = query.paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    pics = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api_v1.get_posts', page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api_v1.get_posts', page=page+1)
    return jsonify({
        'posts': [pic.to_json() for pic in pics],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })