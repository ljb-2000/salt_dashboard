#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#  tanyewei@gmail.com
#  2013/12/04 11:45
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask.ext.migrate import Migrate
from flask.ext import login
from flask.ext.babelex import Babel

app = Flask(__name__)
babel = Babel(app, default_locale='zh')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://salt:ronaldo@172.16.10.85:3306/salt'
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = 'qOH7fBkvial$%P^kWq3#J30gqMiV0rbQ'
db = SQLAlchemy()
db.app = app
db.init_app(app)
migrate = Migrate(app, db)
manager = Manager(app)
from app.models import User


def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(User).get(user_id)


init_login()
### salt ###
from salt.client.api import APIClient


def tokenify(cmd, token=None):
    if token is not None:
        cmd['token'] = token
    return cmd


client = APIClient()
creds = client.create_token(
    creds=dict(
        username='openwrt',
        password='openwrt',
        eauth='pam',
    )
)
###
from app import admin