from flask import Blueprint

api = Blueprint('api_v1', __name__)

from . import authentication, posts, users, comments, errors, funpic, updown
