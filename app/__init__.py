import os

from flask import Flask
from . import db, auth, blog


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY = 'dev',
        DATABASE = os.path.join(app.instance_path, 'app.sqlite'),
    )
    if test_config is None:
        # 在不进行测试时，加载实例配置
        app.config.from_pyfile('config.py', silent=True)
    else:
        # 如果传入，则加载测试配置
        app.config.from_mapping(test_config)
    # 确保实例文件夹存在
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    db.init_app(app)

    app.register_blueprint(auth.bp)

    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app
