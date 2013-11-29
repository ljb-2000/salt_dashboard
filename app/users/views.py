#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#  tanyewei@gmail.com
#  2013/11/26 14:25
from flask.ext import admin, login
from flask.ext.admin import expose
from app import app
from app.users.forms import RegistrationForm, LoginForm
from flask.ext.admin import helpers, expose, BaseView
from flask import request, redirect, url_for, render_template


class MyAdminIndexView(admin.AdminIndexView):
    @expose('/')
    def home(self):
        return self.render('users/home.html')

    def is_accessible(self):
        return login.current_user.is_authenticated()


@app.route('/login/', methods=('GET', 'POST'))
def login_view():
    form = LoginForm(request.form)
    if helpers.validate_form_on_submit(form):
        user = form.get_user()
        login.login_user(user)
        return redirect('/admin/')
    return render_template('form.html', form=form)


@app.route('/logout/')
def logout_view():
    login.logout_user()
    return redirect('/')