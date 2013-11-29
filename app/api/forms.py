#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#  tanyewei@gmail.com
#  2013/11/28 18:51
from wtforms import form, fields, validators


class RunForm(form.Form):
    function = fields.TextField(validators=[validators.required()])
    arguments = fields.TextField(validators=[validators.required()])