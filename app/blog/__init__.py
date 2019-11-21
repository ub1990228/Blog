# _*_ coding:utf-8 _*_
from flask import Blueprint

blog = Blueprint('blog', __name__)

import app.blog.views
