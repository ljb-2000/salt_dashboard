#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#  tanyewei@gmail.com
#  2013/11/26 14:16
import os

_basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = False

ADMINS = frozenset(['tanyewei@gmail.com'])
SECRET_KEY = 'qOH7fBkvial$%P^kWq3#J30gqMiV0rbQ'

SQLALCHEMY_DATABASE_URI = 'mysql://salt:D215&ARm!cm63wf%@172.16.10.85:3306/salt'
SQLALCHEMY_ECHO = False
DATABASE_CONNECT_OPTIONS = {}

THREADS_PER_PAGE = 8

CSRF_ENABLED = True
CSRF_SESSION_KEY = "2nLh6TULFQOMSPrsi21bXfXh2OIwrDId"