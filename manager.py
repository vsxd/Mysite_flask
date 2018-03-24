from app import create_app, db
from app.models import User, Role, Post
from flask_script import Manager, Shell
from flask_migrate import MigrateCommand, Migrate


app = create_app('default')
manager = Manager(app)
migrate = Migrate(app, db)


@staticmethod
def generate_fake_user(count=100):
    from sqlalchemy.exc import IntegrityError
    from random import seed
    import forgery_py

    seed()
    for i in range(count):
        u = User(email=forgery_py.internet.email_address(),
                 username=forgery_py.internet.user_name(True),
                 password=forgery_py.lorem_ipsum.word(),
                 confirmed=True,
                 name=forgery_py.name.full_name(),
                 location=forgery_py.address.city(),
                 about_me=forgery_py.lorem_ipsum.sentence(),
                 member_since=forgery_py.date.date(True))
        db.session.add(u)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


@staticmethod
def generate_fake_post(count=100):
    from random import seed, randint
    import forgery_py

    seed()
    user_count = User.query.count()
    for i in range(count):
        u = User.query.offset(randint(0, user_count-1)).first()
        p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                 timestamp=forgery_py.date.date(True),
                 author=u)
        db.session.add(p)
        db.session.commit()


User.generate_fake = generate_fake_user
Post.generate_fake = generate_fake_post


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Post=Post)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    manager.run()
