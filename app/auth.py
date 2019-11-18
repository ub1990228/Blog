import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from app.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


"""
注册
1、@bp.route 关联了 URL /register 和 register 视图函数。当 Flask 收到一个指向 /auth/register 的请求时就会调用 register 视图并把其返回值作为响应。
2、如果用户提交了表单，那么 request.method 将会是 'POST' 。这咱情况下 会开始验证用户的输入内容。
3、request.form 是一个特殊类型的 dict ，其映射了提交表单的键和值。表单中，用户将会输入其 username 和 password 。
4、验证 username 和 password 不为空。
5、通过查询数据库，检查是否有查询结果返回来验证 username 是否已被注册。 db.execute 使用了带有 ? 占位符 的 SQL 查询语句。占位符可以代替后面的元组参数
中相应的值。使用占位符的 好处是会自动帮你转义输入值，以抵御 SQL 注入攻击 。
fetchone() 根据查询返回一个记录行。 如果查询没有结果，则返回 None 。后面还用到 fetchall() ，它返回包括所有结果的列表。
6、如果验证成功，那么在数据库中插入新用户数据。为了安全原因，不能把密码明文 储存在数据库中。相代替的，使用 generate_password_hash() 生成安全的哈希值并
储存 到数据库中。查询修改了数据库是的数据后使用 meth:db.commit() <sqlite3.Connection.commit> 保存修改。
7、用户数据保存后将转到登录页面。 url_for() 根据登录视图的名称生成相应的 URL 。与写固定的 URL 相比， 这样做的好处是如果以后需要修改该视图相应的 URL ，
那么不用修改所有涉及到 URL 的代码。 redirect() 为生成的 URL 生成一个重定向响应。
8、如果验证失败，那么会向用户显示一个出错信息。 flash() 用于储存在渲染模块时可以调用的信息。
9、当用户最初访问 auth/register 时，或者注册出错时，应用显示一个注册 表单。 render_template() 会渲染一个包含 HTML 的模板。
"""
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


"""
登录
首先需要查询用户并存放在变量中，以备后用。
check_password_hash() 以相同的方式哈希提交的 密码并安全的比较哈希值。如果匹配成功，那么密码就是正确的。
session 是一个 dict ，它用于储存横跨请求的值。当验证 成功后，用户的 id 被储存于一个新的会话中。会话数据
被储存到一个 向浏览器发送的 cookie 中，在后继请求中，浏览器会返回它。 Flask 会安全对数据进行 签名 以防数
据被篡改。现在用户的 id 已被储存在 session 中，可以被后续的请求使用。 请每个请求的开头，如果用户已登录，
那么其用户信息应当被载入，以使其可用于 其他视图。
"""
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


"""
bp.before_app_request() 注册一个 在视图函数之前运行的函数，不论其 URL 是什么。 load_logged_in_user 
检查用户 id 是否已经储存在 session 中，并从数据库中获取用户数据，然后储存在 g.user 中。 g.user 的持续
时间比请求要长。 如果没有用户 id ，或者 id 不存在，那么 g.user 将会是 None 。
"""
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


"""
注销
注销的时候需要把用户 id 从 session 中移除。 然后 load_logged_in_user 就不会在后继请求中载入用户了。
"""
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

"""
用户登录以后才能创建、编辑和删除博客帖子。在每个视图中可以使用 装饰器 来完成这个工作。
装饰器返回一个新的视图，该视图包含了传递给装饰器的原视图。新的函数检查用户 是否已载入。如果已载入，那么就继续正常执行原视图，
否则就重定向到登录页面。 我们会在博客视图中使用这个装饰器。
"""
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
