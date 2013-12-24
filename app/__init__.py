#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#  tanyewei@gmail.com
#  2013/12/04 11:45
import salt.client
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask.ext.migrate import Migrate
from flask.ext import login
from flask.ext.babelex import Babel
from redis import Redis
import logging
import yaml

app = Flask(__name__)

app.config.from_pyfile('../config.cfg')
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
babel = Babel(app, default_locale=app.config['BABEL_LOCALE'])
db = SQLAlchemy()
db.app = app
db.init_app(app)
migrate = Migrate(app, db)
manager = Manager(app)
client = salt.client.LocalClient()
redis_cli = Redis(host=app.config['REDIS_HOST'], port=app.config['REDIS_PORT'], password=app.config['REDIS_PASSWORD'])
from app.models import User

import collections


def convert(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(convert, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(convert, data))
    else:
        return data


@app.template_filter('output')
def output(data):
    return yaml.dump(convert(data), default_flow_style=False)


app.jinja_env.filters['output'] = output


def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(User).get(user_id)


init_login()
from app import admin
