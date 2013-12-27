#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#  tanyewei@gmail.com
#  2013/12/04 13:58
import json
from app.models import Host
from app import client
from flask import url_for, request, flash, redirect
from flask.ext import login
from flask.ext.admin import expose, BaseView, helpers
from flask.ext.admin.contrib import sqla
from flask.ext.admin.actions import action
from app.models import User, Returner
from werkzeug.security import generate_password_hash
from flask.ext.admin.contrib.sqla.tools import get_query_for_ids
from app.forms import CommandForm
from app.util import AESdecrypt, run_async
from app import db
from jinja2 import Markup
from flask.ext.admin.contrib.fileadmin import FileAdmin


class HostModelView(sqla.ModelView):
    column_filters = (('group.name'), )
    column_searchable_list = ('name', Host.name)
    from app.models import Grains

    inline_models = (Grains,)
    column_labels = dict(
        group=u'群组', name=u'主机名', description=u'描述', public_ip=u'公网地址(电信)',
        public_ip_secondary=u'公网地址(联通)', private_ip=u'私网地址', saltversion=u'salt版本')

    @action(name='saltstack', text=u'saltstack', confirmation=None)
    def saltstack(self, ids):
        hosts = get_query_for_ids(self.get_query(), self.model, ids).all()
        return self.render('saltstack/action.html', hosts=hosts)


    @expose('/action/run/', methods=('POST',))
    def run(self):
        tgt, fun, args = request.json['tgt'], request.json['fun'], request.json['args']
        ret = run_async(tgt, fun, args, expr_form='list')
        return str(ret)
        #


    def is_accessible(self):
        return login.current_user.is_authenticated()


class HostGroupModelView(sqla.ModelView):
    column_labels = dict(
        name=u'群组名', description=u'描述', groups=u'组成员')

    def is_accessible(self):
        return login.current_user.is_authenticated()


class JobModelView(sqla.ModelView):
    def _jid_formatter(view, context, model, name):
        return Markup(
            "<a href='%s'>%s</a>" % (
                model.jid, model.jid
            )
        ) if model.jid else ""

    can_create = False
    column_default_sort = ('jid', True)
    column_labels = dict(id='ID', jid='JID')
    column_formatters = {'jid': _jid_formatter}
    column_display_pk = True
    column_searchable_list = ('jid', Returner.jid)

    def is_accessible(self):
        return login.current_user.is_authenticated()


class UserModelView(sqla.ModelView):
    column_searchable_list = ('login', User.login)
    column_filters = (User.login, )
    column_exclude_list = ('password')
    column_labels = dict(login=u'登录名', email=u'邮件地址', password=u'密码')

    def is_accessible(self):
        return login.current_user.is_authenticated()

    def on_model_change(self, form, model, is_created=True):
        if form.data.has_key('password'):
            model.password = generate_password_hash(form.data['password'])


class SaltView(BaseView):
    def is_accessible(self):
        return login.current_user.is_authenticated()

    @expose('/', methods=('GET', 'POST'))
    def index(self):
        form = CommandForm(request.form)
        if helpers.validate_form_on_submit(form):
            if form.args.data != "":
                ret = client.cmd_async(tgt=str(form.tgt.data).strip(), fun=str(form.fun.data).strip(),
                                       arg=str(form.args.data).strip().split(';'),
                                       expr_form='compound', ret='http_api')
            else:
                ret = client.cmd_async(tgt=str(form.tgt.data).strip(), fun=str(form.fun.data).strip(),
                                       expr_form='compound', ret='http_api')
            flash(str(ret), 'success')
        jobs = Returner.query.order_by(Returner.id.desc()).limit(10).all()
        return self.render('saltstack/command.html', form=form, jobs=jobs)

    @expose('/view/<jid>')
    def run(self, jid):
        ret = Returner().query.filter_by(jid=jid).first()
        if ret:
            data = ret.read_ret(jid)
            return self.render('saltstack/job.html', data=data)
        else:
            return 'not found'

    @expose('/test')
    def test(self):
        return self.render('saltstack/test.html')


from app import app


@app.route('/salt/api/ret', methods=['POST'])
def ret():
    data = request.form.get('data', None)
    ret = AESdecrypt('Oc0riQA3pFyQmvI4', data)
    data = eval(ret)
    minion = Returner().query.filter_by(jid=data['jid']).first()
    if minion:
        minion.write_ret(ret=data)
    else:
        minion = Returner(fun=data['fun'], jid=data['jid'])
        db.session.add(minion)
        db.session.commit()
        minion.write_ret(ret=data)
    return 'ok'


import os
from flask.ext.admin.babel import gettext


class FileManage(FileAdmin):
    allowed_extensions = ('swf', 'jpg', 'gif', 'png')
    editable_extensions = ('md', 'html', 'txt')
    edit_template = 'admin/edit.html'

    @expose('/edit/', methods=('GET', 'POST'))
    def edit(self):
        """
            Edit view method
        """
        path = request.args.getlist('path')
        next_url = None
        if not path:
            return redirect(url_for('.index'))

        if len(path) > 1:
            next_url = url_for('.edit', path=path[1:])
        path = path[0]

        base_path, full_path, path = self._normalize_path(path)

        if not self.is_accessible_path(path):
            flash(gettext(gettext('Permission denied.')))
            return redirect(self._get_dir_url('.index'))

        dir_url = self._get_dir_url('.index', os.path.dirname(path))
        next_url = next_url or dir_url

        from app.forms import CKEditForm

        form = CKEditForm(helpers.get_form_data())
        error = False

        if helpers.validate_form_on_submit(form):
            form.process(request.form, content='')
            if form.validate():
                try:
                    with open(full_path, 'w') as f:
                        f.write(request.form['content'].encode('UTF-8'))
                except IOError:
                    flash(gettext("Error saving changes to %(name)s.", name=path), 'error')
                    error = True
                else:
                    self.on_edit_file(full_path, path)
                    flash(gettext("Changes to %(name)s saved successfully.", name=path))
                    return redirect(next_url)
        else:
            try:
                with open(full_path, 'r') as f:
                    content = f.read()
            except IOError:
                flash(gettext("Error reading %(name)s.", name=path), 'error')
                error = True
            except:
                flash(gettext("Unexpected error while reading from %(name)s", name=path), 'error')
                error = True
            else:
                try:
                    content = content.decode('utf8')
                except UnicodeDecodeError:
                    flash(gettext("Cannot edit %(name)s.", name=path), 'error')
                    error = True
                except:
                    flash(gettext("Unexpected error while reading from %(name)s", name=path), 'error')
                    error = True
                else:
                    form.content.data = content

        return self.render(self.edit_template, dir_url=dir_url, path=path,
                           form=form, error=error)

    def is_accessible(self):
        return login.current_user.is_authenticated()