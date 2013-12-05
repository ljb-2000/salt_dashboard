#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#  tanyewei@gmail.com
#  2013/12/04 11:48
import app
#from app import app, manager
from flask.ext.migrate import MigrateCommand

app.manager.add_command('db', MigrateCommand)

app.debug = True
app.manager.run()