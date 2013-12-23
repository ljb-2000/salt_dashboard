#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#  tanyewei@gmail.com
#  2013/12/04 13:53
from wtforms import form, fields, validators, SelectMultipleField, widgets, HiddenField
from werkzeug.security import check_password_hash
from app.models import User
from app import db


class LoginForm(form.Form):
    login = fields.TextField(u'用户名', validators=[validators.required()])
    password = fields.PasswordField(u'密码',validators=[validators.required()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('用户名或密码错误!')
            #if user.password != generate_password_hash(self.password.data):
        if not check_password_hash(user.password, self.password.data):
            raise validators.ValidationError('用户名或密码错误!')

    def get_user(self):
        return db.session.query(User).filter_by(login=self.login.data).first()


class RegistrationForm(form.Form):
    login = fields.TextField(validators=[validators.required()])
    email = fields.TextField()
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        if db.session.query(User).filter_by(login=self.login.data).count() > 0:
            raise validators.ValidationError('Duplicate username')


class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


def SaltForm(form, choices):
    class _SaltForm(form.Form):
        action = HiddenField(default='salt')
        expr_form = fields.SelectField(u'Target Format', choices=[['List', 'list']])
        tgt = MultiCheckboxField(u'Target', choices=choices, default=[key for key, value in choices])
        fun = fields.StringField(u'Function', validators=[validators.required()])
        arg = fields.StringField(u'Arguments', validators=[validators.required()])

    return _SaltForm(form)


class TestForm(form.Form):
    #action = HiddenField(default='salt')
    #expr_form = fields.SelectField(u'Target Format', choices=[['List', 'list']])
    tgt = MultiCheckboxField(u'Target', validators=[validators.DataRequired()])
    fun = fields.StringField(u'Function', validators=[validators.InputRequired()])
    arg = fields.StringField(u'Arguments', validators=[validators.InputRequired()])


class CommandForm(form.Form):
    tgt = fields.StringField(u'Targeting', validators=[validators.InputRequired(u'目标主机为必须的')])
    fun = fields.StringField(u'Function', validators=[validators.InputRequired(u'执行模块为必须的')])
    arg = fields.StringField(u'Arguments')