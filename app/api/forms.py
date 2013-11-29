#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#  tanyewei@gmail.com
#  2013/11/28 18:51
from wtforms import form, fields, validators


class RunForm(form.Form):
    command = fields.TextField(validators=[validators.required()])
    xx = fields.SelectField(validators=[validators.required()], choices=[('x', '1')])
    oo = fields.SelectMultipleField(choices=[('x', '1'), ('haha', 'HAHA')])
    aa = fields.RadioField(choices=[('x', '1'), ('haha', 'HAHA')])