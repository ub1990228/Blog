# _*_ codding:utf-8 _*_
from flask_script import Manager, Shell
from app import create_app, db
# 需要导入所有models下的类，否则数据库迁移不成功（找不到）
from app.models import *
from flask_migrate import Migrate, MigrateCommand

app = create_app('default')
manager = Manager(app)
# 使用Migrate绑定app和db
migrate = Migrate(app, db)


# 每次启动shell都要导入数据库实例和模型，为了避免一直重复导入，我们可以让flask-script的shell命令自动导入特定的对象。
# 若要把对象添加到导入列表中，我们要为shell命令注册一个make_context回调函数
def make_shell_context():
    return dict(app=app, db=db)  # 注册程序、数据库实例


# 添加迁移脚本的命令到manager中
# MigarateCommand会去读取当前导入的数据模型并映射到数据库中
manager.add_command('db', MigrateCommand)
manager.add_command("shell", Shell(make_context=make_shell_context))


if __name__ == '__main__':
    manager.run()
