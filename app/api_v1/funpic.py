from flask import jsonify, request, url_for, current_app
from ..models import FunPic
from . import api


@api.route('/funpic/funny')
def get_funny():
    page = request.args.get('page', 1, type=int)
    query = FunPic.query.filter_by(info='good').filter_by(type='funny')
    pagination = query.paginate(
        page, per_page=current_app.config['PIC_PER_PAGE'],
        error_out=False)
    pics = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api_v1.get_posts', page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api_v1.get_posts', page=page+1)
    return jsonify({
        'pics': [pic.to_json() for pic in pics],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/funpic/girls')
def get_girls():
    page = request.args.get('page', 1, type=int)
    query = FunPic.query.filter_by(info='good').filter_by(type='girls')
    pagination = query.paginate(
        page, per_page=current_app.config['PIC_PER_PAGE'],
        error_out=False)
    pics = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api_v1.get_girls', page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api_v1.get_girls', page=page+1)
    return jsonify({
        'pics': [pic.to_json() for pic in pics],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })
