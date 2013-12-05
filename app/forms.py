#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#  tanyewei@gmail.com
#  2013/12/04 13:53
from wtforms import form, fields, validators, SelectMultipleField, widgets, HiddenField
from werkzeug.security import check_password_hash
from app_test.users.models import User
from app_test import db


class LoginForm(form.Form):
    login = fields.TextField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Invalid user')
            #if user.password != generate_password_hash(self.password.data):
        if not check_password_hash(user.password, self.password.data):
            raise validators.ValidationError('Invalid password')

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


def SaltForm(choices):
    class _SaltForm(form.Form):
        action = HiddenField(default='salt')
        minion = MultiCheckboxField(choices=choices, default=[key for key, value in choices])
        command = fields.StringField(validators=[validators.required()])
        args = fields.StringField(validators=[validators.required()])

    return _SaltForm()