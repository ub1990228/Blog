# _*_ coding:utf-8 _*_
import functools
from flask import (
    flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from app.models import User, Post
from . import auth
from app import db


@auth.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        # 查询name=username的第一条数据
        elif db.session.query(User).filter(User.username == username).first() is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            # 生成你要创建的数据对象
            obj = User(username=username, password=password)
            # 把要创建的数据对象添加到这个session里
            db.session.add(obj)
            # 统一提交，创建数据
            db.session.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@auth.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        # 查询数据库里username的第一条数据
        user = db.session.query(User).filter(User.username == username).first()
        if user is None:
            error = 'Incorrect username.'
        # 查到的数据不能['password']需要使用.password
        # elif not check_password_hash(user.password, password):
        elif not user.password == password:
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('blog.index'))

        flash(error)

    return render_template('auth/login.html')


@auth.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = db.session.query(User).filter(User.id == user_id).first()


@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('blog.index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
