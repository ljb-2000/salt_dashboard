#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#  tanyewei@gmail.com
#  2013/12/04 13:58
from app.models import Host
from app import client
from flask import url_for, request, flash
from flask.ext import login
from flask.ext.admin import expose
from flask.ext.admin.contrib import sqla
from flask.ext.admin.actions import action
from app.models import User
from werkzeug.security import generate_password_hash
from flask.ext.admin.contrib.sqla.tools import get_query_for_ids

from app.forms import SaltForm


class HostModelView(sqla.ModelView):
    column_labels = dict(
        group=u'群组', name=u'主机名', description=u'描述', public_ip=u'公网地址(电信)',
        public_ip_secondary=u'公网地址(联通)', private_ip=u'私网地址', saltversion=u'salt版本')

    action_view = None

    @action(name='saltstack', text=u'saltstack', confirmation=None)
    def saltstack(self, ids):
        hosts = get_query_for_ids(self.get_query(), self.model, ids).all()
        choices = []
        [choices.append([str(host.id), str(host.name)]) for host in hosts]
        form = SaltForm(choices=choices)
        return self.render('saltstack.html', form=form)


    @expose('/action/', methods=('POST',))
    def action_view(self):
        if request.form.get('action') == 'salt':
            tgt = request.form.getlist('tgt')
            fun = request.form.get('fun')
            arg = request.form.getlist('arg')
            expr_form = request.form.get('expr_form')

            a = lambda x: Host.query.filter_by(id=int(x)).first().name
            target = map(a, tgt)
            tgts = ''
            for x in target: tgts += x + ','
            ret = client.cmd(tgts, fun, arg, expr_form='expr_form')
            return flash(str(ret))
        return self.handle_action()

    @expose('/api/')
    def api(self):
        return 'test'

    def is_accessible(self):
        return login.current_user.is_authenticated()


class HostGroupModelView(sqla.ModelView):
    column_labels = dict(
        name=u'群组名', description=u'描述', groups=u'组成员')

    def is_accessible(self):
        return login.current_user.is_authenticated()


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