#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#  tanyewei@gmail.com
#  2013/11/26 14:19
from app import db
from flask.ext.admin.contrib import sqla
from flask.ext import login
from werkzeug.security import generate_password_hash


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(66))

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    # Required for administrative interface
    def __unicode__(self):
        return self.username


class UserModelView(sqla.ModelView):
    column_searchable_list = ('login', User.login)
    column_filters = ('login', User.login)
    column_exclude_list = ('password')
    column_labels = dict(login=u'登录名', email=u'邮件地址', password=u'密码')

    def is_accessible(self):
        return login.current_user.is_authenticated()

    def on_model_change(self, form, model, is_created=True):
        if form.data.has_key('password'):
            model.password = generate_password_hash(form.data['password'])