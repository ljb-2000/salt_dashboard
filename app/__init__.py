#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#  tanyewei@gmail.com
#  2013/11/26 14:13
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext import admin, login
from flask.ext.babelex import Babel


def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(User).get(user_id)


app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
babel = Babel(app)


@babel.localeselector
def get_locale():
    # Put your logic here. Application can store locale in
    # user profile, cookie, session, etc.
    return 'zh'


init_login()

from app.users.views import MyAdminIndexView
from app.users.models import User, UserModelView
from app.hosts.views import HostModelView, HostGroupModelView
from app.hosts.models import Host, HostGroup

admin = admin.Admin(app, 'Salt Admin', index_view=MyAdminIndexView())
admin.add_view(UserModelView(User, db.session, name=u'用户管理', endpoint='users'))
admin.add_view(HostModelView(Host, db.session, name=u'主机', category=u'主机管理', endpoint='hosts'))
admin.add_view(HostGroupModelView(HostGroup, db.session, name=u'群组', category=u'主机管理', endpoint='groups'))