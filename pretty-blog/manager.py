# coding=utf-8

from flask_script import Manager, Shell
from app import create_app, db
from flask_migrate import Migrate, MigrateCommand
from app.models import User, Role, Post


app = create_app("default")

manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(db=db, app=app, User=User, Role=Role, Post=Post)

manager.add_command("shell", Shell(make_context=make_shell_context))  ##
manager.add_command("db", MigrateCommand)


if __name__ == "__main__":
    manager.run()