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

app = Flask(__name__)

app.config.from_pyfile('../config.cfg')
babel = Babel(app, default_locale=app.config['BABEL_LOCALE'])
db = SQLAlchemy()
db.app = app
db.init_app(app)
migrate = Migrate(app, db)
manager = Manager(app)
client = salt.client.LocalClient()
redis_cli = Redis(host=app.config['REDIS_HOST'], port=app.config['REDIS_PORT'], password=app.config['REDIS_PASSWORD'])
from app.models import User

# ssl
from OpenSSL import SSL

ctx = SSL.Context(SSL.SSLv23_METHOD)
ctx.use_privatekey_file('cert/ssl.key')
ctx.use_certificate_file('cert/ssl.cert')


def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(User).get(user_id)


init_login()
from app import admin
