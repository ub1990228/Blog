# -*- coding=utf-8 -*-
import os


class Config:
    SECRET_KEY = os.urandom(24)
    """
    动态追踪修改
    """
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@127.0.0.1:3306/blog'
    DEBUG = True


config = {
    'default': DevelopmentConfig
}
