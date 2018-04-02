from flask import Blueprint

updown = Blueprint('funpic', __name__)

from . import views
