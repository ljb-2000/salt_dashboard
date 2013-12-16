#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#  tanyewei@gmail.com
#  2013/12/04 11:45
#import salt.client
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask.ext.migrate import Migrate
from flask.ext import login
from flask.ext.babelex import Babel

app = Flask(__name__)
babel = Babel(app, default_locale='zh')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:sdksjd###sadj@44@172.16.10.85:3306/salt'
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = 'qOH7fBkvial$%P^kWq3#J30gqMiV0rbQ'
db = SQLAlchemy()
db.app = app
db.init_app(app)
migrate = Migrate(app, db)
manager = Manager(app)
#client = salt.client.LocalClient()
from app.models import User


def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(User).get(user_id)


init_login()
from app import admin