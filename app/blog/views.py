# _*_ coding:utf-8 _*_
from app.auth.views import login_required
from flask import (
    flash, g, redirect, render_template, request, url_for
)
from sqlalchemy import desc
from werkzeug.exceptions import abort
from app.models import User, Post
from . import blog
from app import db


@blog.route('/')
def index():
    posts = db.session.query(Post.id, Post.title, Post.body, Post.created, Post.author_id). \
        join(User).filter(Post.author_id == User.id).order_by(desc(Post.id)).all()
    return render_template('blog/index.html', posts=posts)


@blog.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            obj = Post(title=title, body=body, author_id=g.user.id)
            db.session.add(obj)
            db.session.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


def get_post(id, check_author=True):
    post = db.session.query(Post.id, Post.title, Post.body, Post.author_id).\
        join(User).filter(Post.author_id == User.id, Post.id == id).first()
    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post.author_id != g.user.id:
        abort(403)

    return post


@blog.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db.session.query(Post).filter(Post.id == id).update({'title': title, 'body': body})
            db.session.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@blog.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db.session.query(Post).filter(Post.id == id).delete()
    db.session.commit()
    return redirect(url_for('blog.index'))
