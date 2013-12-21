#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#  tanyewei@gmail.com
#  2013/12/04 13:58
from app.models import Host
#from app import client
from flask import url_for, request, flash, redirect, jsonify
from flask.ext import login
from flask.ext.admin import expose, BaseView, helpers
from flask.ext.admin.contrib import sqla
from flask.ext.admin.actions import action
from app.models import User, Returner
from werkzeug.security import generate_password_hash
from flask.ext.admin.contrib.sqla.tools import get_query_for_ids
from app.forms import SaltForm, TestForm, MultiCheckboxField, CommandForm
from app.util import AESdecrypt
from app import db
from jinja2 import Markup


class HostModelView(sqla.ModelView):
    #column_exclude_list = ('grains')
    #form_overrides = dict(name=FileField)
    column_filters = ('group', )
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
    column_filters = ('login', User.login)
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
        #ret = client.cmd_async(tgts, fun, arg, expr_form=expr_form)
        if helpers.validate_form_on_submit(form):
            from app import client
            ret = client.cmd_async(tgt=form.tgt.data, fun=form.fun.data, arg=form.arg.data.split(';'), expr_form='compound', ret='http_ret')
            flash(str(ret))
        jobs = Returner.query.order_by(Returner.id.desc()).limit(10).all()
        return self.render('saltstack/command.html', form=form, jobs=jobs)

    @expose('/view/<jid>')
    def run(self, jid):
        if jid:
            ret = Returner().query.filter_by(jid=jid).first()
            data = ret.read_ret(jid)
            if ret:
                return self.render('saltstack/job.html', data=data)


from app import app


@app.route('/salt/api/ret', methods=['POST'])
def ret():
    data = request.form.get('data', None)
    ret = AESdecrypt('Oc0riQA3pFyQmvI4', data)
    data = eval(ret)
    minion = Returner().query.filter_by(jid=data['jid']).first()
    if minion:
        print 'save minion id:', minion.id
        minion.write_ret(ret=data)
    else:
        minion = Returner(jid=data['jid'])
        print 'new minion id:', minion.id
        db.session.add(minion)
        db.session.commit()
        minion.write_ret(ret=data)
    return 'ok'