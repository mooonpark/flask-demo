# coding:utf-8
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from . import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)

    @property
    def password(self):
        raise AttributeError(u"无法获取密码")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirm_token(self, expiration=3600):
        s = Serializer(current_app.config["SECRET_KEY"], expiration)
        return s.dumps({"confirm": self.id})

    def confirm(self, token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
        except:
            return False
        if self.id != data.get("confirm"):
            return False
        self.confirmed = True
        ##care
        db.session.add(self)
        db.session.commit()
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config["SECRET_KEY"], expiration)
        return s.dumps({"reset": self.id})

    def verify_reset(self, token, new_password):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get("reset") != self.id:
            return False
        #用self.password修改密码
        self.password = new_password
        db.session.add(self)
        db.session.commit()
        return True

    def __repr__(self):
        return "<User %s>" % self.name

    def generate_email_token(self, email, expiration=3600):
        s = Serializer(current_app.config["SECRET_KEY"], expiration)
        #not s.dumps({}, {})
        return s.dumps({"change_email":self.id, "new_email":email})

    def verify_email(self, token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get("change_email") == self.id:
            #判断get有无
            new_email = data.get("new_email")
            if new_email is None:
                return False
            #self.query
            if self.query.filter_by(email=new_email).first():
                return False
            self.email = new_email
            db.session.add(self)
            db.session.commit()
            return True
        else:
            return False

class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
