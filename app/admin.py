#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#  tanyewei@gmail.com
#  2013/12/04 15:03
from app import app, db
from flask import redirect, url_for, request
from flask.ext import login
from flask.ext.admin import Admin, AdminIndexView, expose, helpers
from flask.ext.admin.contrib import sqla

from app.forms import LoginForm, RegistrationForm
from app.models import User, Host, HostGroup, Returner

from app.util import ssl_required

class MyModelView(sqla.ModelView):
    def is_accessible(self):
        return login.current_user.is_authenticated()


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated():
            return redirect(url_for('.login_view'))
        return super(MyAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    @ssl_required
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login.login_user(user)

        if login.current_user.is_authenticated():
            return redirect(url_for('.index'))
        #link = '<p>Don\'t have an account? <a href="' + url_for('.register_view') + '">Click here to register.</a></p>'
        self._template_args['form'] = form
        #self._template_args['link'] = link
        return super(MyAdminIndexView, self).index()

    #@expose('/register/', methods=('GET', 'POST'))
    def register_view(self):
        form = RegistrationForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = User()

            form.populate_obj(user)

            db.session.add(user)
            db.session.commit()

            login.login_user(user)
            return redirect(url_for('.index'))
        link = '<p>Already have an account? <a href="' + url_for('.login_view') + '">Click here to log in.</a></p>'
        self._template_args['form'] = form
        self._template_args['link'] = link
        return super(MyAdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('.index'))


def add():
    from app.models import User
    from werkzeug.security import generate_password_hash

    user = User()
    user.login = 'admin'
    user.email = 'tanyewei@gmail.com'
    user.password = generate_password_hash('admin')
    from app import db

    db.session.add(user)
    db.session.commit()


from app.views import UserModelView, HostModelView, HostGroupModelView, SaltView, JobModelView

#add()
admin = Admin(app, "Salt Admin", index_view=MyAdminIndexView())
admin.add_view(UserModelView(User, db.session, name=u'用户管理', endpoint='user'))
admin.add_view(HostModelView(Host, db.session, name=u'主机', category=u'主机管理', endpoint='host'))
admin.add_view(HostGroupModelView(HostGroup, db.session, name=u'群组', category=u'主机管理', endpoint='group'))
admin.add_view(SaltView(name=u'执行命令', endpoint='salt', category='saltstack'))
admin.add_view(JobModelView(Returner, db.session, endpoint='salt/view', name=u'任务查看', category='saltstack'))