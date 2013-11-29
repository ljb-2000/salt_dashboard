#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#  tanyewei@gmail.com
#  2013/11/26 14:54
from flask.ext import login
from flask.ext.admin.contrib import sqla
from flask.ext.admin.actions import action
from flask.ext.admin import expose
from flask import request, url_for
from flask.ext.admin.contrib.sqla.tools import is_inherited_primary_key, get_column_for_current_model, get_query_for_ids


class HostModelView(sqla.ModelView):
    column_labels = dict(
        group=u'群组', name=u'主机名', description=u'描述', public_ip=u'公网地址(电信)',
        public_ip_secondary=u'公网地址(联通)', private_ip=u'私网地址', saltversion=u'salt版本')

    @action(name='salt_run', text=u'salt_run', confirmation=None)
    def run(self, ids):
        print ids
        from app.api.forms import RunForm

        form = RunForm()
        hosts = get_query_for_ids(self.get_query(), self.model, ids).all()
        for host in hosts:
            print host.id
        url = url_for('hosts.api')
        return self.render('salt/command.html', form=form, action=url, hosts=hosts)


    @expose('/api/', methods=('POST',))
    def api(self):
        print request.form
        return 'good'

    def is_accessible(self):
        return login.current_user.is_authenticated()


class HostGroupModelView(sqla.ModelView):
    column_labels = dict(
        name=u'群组名', description=u'描述', groups=u'组成员')

    def is_accessible(self):
        return login.current_user.is_authenticated()