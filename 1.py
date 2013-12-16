#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#  tanyewei@gmail.com
#  2013/12/13 22:57
from flask import Flask
from flask.ext.admin import Admin

app = Flask(__name__)

admin = Admin(app)
# Add administrative views here

app.run()