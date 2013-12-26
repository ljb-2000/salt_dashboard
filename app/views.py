#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#  tanyewei@gmail.com
#  2013/12/04 13:58
from app.models import Host
from app import client
from flask import url_for, request, flash, redirect, jsonify
from flask.ext import login
from flask.ext.admin import expose, BaseView, helpers
from flask.ext.admin.contrib import sqla
from flask.ext.admin.actions import action
from app.models import User, Returner, HostGroup
from werkzeug.security import generate_password_hash
from flask.ext.admin.contrib.sqla.tools import get_query_for_ids
from app.forms import SaltForm, TestForm, MultiCheckboxField, CommandForm
from app.util import AESdecrypt
from app import db
from jinja2 import Markup
from flask.ext.admin.contrib.fileadmin import FileAdmin


class HostModelView(sqla.ModelView):
    #column_exclude_list = ('grains')
    #form_overrides = dict(name=FileField)
    column_filters = (('group.name'), )
    column_searchable_list = ('name', Host.name)
    from app.models import Grains

    inline_models = (Grains,)
    column_labels = dict(
        group=u'群组', name=u'主机名', description=u'描述', public_ip=u'公网地址(电信)',
        public_ip_secondary=u'公网地址(联通)', private_ip=u'私网地址', saltversion=u'salt版本')

    @action(name='saltstack', text=u'saltstack', confirmation=None)
    def saltstack(self, ids):
        '''
        hosts = get_query_for_ids(self.get_query(), self.model, ids).all()
        choices = []
        [choices.append([str(host.id), str(host.name)]) for host in hosts]
        form = SaltForm(choices=choices)

        #return self.render('saltstack.html', form=form)
        '''
        return redirect(url_for('.api', ids=ids))


    @expose('/action/', methods=('POST',))
    def action_view(self):
        '''
        if request.form.get('action') == 'salt':
            tgt = request.form.getlist('tgt')
            fun = request.form.get('fun')
            arg = request.form.getlist('arg')
            expr_form = request.form.get('expr_form')

            a = lambda x: Host.query.filter_by(id=int(x)).first().name
            target = map(a, tgt)
            tgts = ''
            for x in target: tgts += x + ','
            ret = client.cmd_async(tgts, fun, arg, expr_form=expr_form)
            flash(str(ret))
        '''
        return self.handle_action()

    @expose('/api/', methods=('GET', 'POST'))
    def api(self):
        ids = request.args.getlist('ids')
        hosts = get_query_for_ids(self.get_query(), self.model, ids).all()
        x = lambda x, y: [x, y]
        choices = [x(str(host.id), str(host.name)) for host in hosts]
        form = TestForm(request.form)
        form.tgt.choices = choices
        form.tgt.default = [key for key, value in choices]
        form.process()
        if helpers.validate_form_on_submit(form):
            flash('ok')
        return self.render('saltstack.html', form=form)

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
                ret = client.cmd_async(tgt=form.tgt.data, fun=form.fun.data, arg=form.args.data.split(';'),
                                       expr_form='compound', ret='http_api')
            else:
                ret = client.cmd_async(tgt=form.tgt.data, fun=form.fun.data, expr_form='compound', ret='http_api')
            flash(str(ret))
        jobs = Returner.query.order_by(Returner.id.desc()).limit(10).all()
        return self.render('saltstack/command.html', form=form, jobs=jobs)

    @expose('/view/<jid>')
    def run(self, jid):
        if jid:
            ret = Returner().query.filter_by(jid=jid).first()
            if ret:
                data = ret.read_ret(jid)
                return self.render('saltstack/job.html', data=data)
            else:
                return 'not found'


from app import app


@app.route('/salt/api/ret', methods=['POST'])
def ret():
    app.logger.warn(str(request.form))
    data = request.form.get('data', None)
    ret = AESdecrypt('Oc0riQA3pFyQmvI4', data)
    data = eval(ret)
    minion = Returner().query.filter_by(jid=data['jid']).first()
    if minion:
        app.logger.info('save minion id:%s', minion.id)
        minion.write_ret(ret=data)
    else:
        minion = Returner(fun=data['fun'], jid=data['jid'])
        app.logger.info('new minion id:%s', minion.id)
        db.session.add(minion)
        db.session.commit()
        minion.write_ret(ret=data)
    return 'ok'


import os
from flask.ext.admin.contrib.fileadmin import EditForm
from flask.ext.admin.babel import gettext, lazy_gettext


class FileManage(FileAdmin):
    allowed_extensions = ('swf', 'jpg', 'gif', 'png')
    editable_extensions = ('md', 'html', 'txt')

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

        form = EditForm(helpers.get_form_data())
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