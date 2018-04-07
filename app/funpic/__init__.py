from flask import Blueprint

funpic = Blueprint('funpic', __name__)

from . import views
