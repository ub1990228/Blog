# _*_ Coding:utf-8 _*_
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config
db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    db.init_app(app)
    # 蓝图导入不能放在上面，当你从其他模块导入蓝图的时候就需要 db 了，
    # 但是这个时候db 还没有生成，所以会报出错误 提示不可以从当中导入相应的模块
    from app.auth import auth as auth_blueprint
    from app.blog import blog as blog_blueprint
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(blog_blueprint)
    return app
