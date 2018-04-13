from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_pagedown import PageDown
from flask_apscheduler import APScheduler
from config import config

# from app.funpic.spider import girls_pic_scheduler, funny_pic_scheduler

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()
scheduler = APScheduler()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    db.app = app  # prepare for spider to call
    login_manager.init_app(app)
    pagedown.init_app(app)
    scheduler.init_app(app)
    scheduler.start()

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .updown import updown as updown_blueprint
    app.register_blueprint(updown_blueprint, url_prefix='/updown')

    from .funpic import funpic as funpic_blueprint
    app.register_blueprint(funpic_blueprint, url_prefix='/funpic')

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/v1')

    return app
