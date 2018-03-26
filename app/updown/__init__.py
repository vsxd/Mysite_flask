from flask import Blueprint

updown = Blueprint('updown', __name__)

from . import views