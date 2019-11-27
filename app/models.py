from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
"""
先初始化当前的数据库环境
python manager.py db init
初始化当前项目的一个迁移环境，类似git commit -m "'
python manager.py db migrate -m ""
更新数据库
python manager.py db upgrade
"""


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)  # 编号
    username = db.Column(db.String(10), unique=True)  # 用户名
    password = db.Column(db.String(10))  # 密码

    def __repr__(self):
        return "<User %r>" % self.username


class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created = db.Column(db.DateTime, index=True, default=datetime.now)
    title = db.Column(db.Text)
    body = db.Column(db.Text)

    # 密码继续hash加密
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)
