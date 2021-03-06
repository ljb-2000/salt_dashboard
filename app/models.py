#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#  tanyewei@gmail.com
#  2013/12/04 11:49
from app import db
from app import redis_cli
import json


class User(db.Model):
    #inline_models = (UserInfo,)
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(66))

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    # Required for administrative interface
    def __unicode__(self):
        return self.username


class Host(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.Text())
    public_ip = db.Column(db.String(64))
    public_ip_secondary = db.Column(db.String(64))
    private_ip = db.Column(db.String(64))
    group_id = db.Column(db.Integer, db.ForeignKey('host_group.id'))
    saltversion = db.Column(db.String(64), default='0')
    group = db.relationship('HostGroup', backref='groups')


    def __unicode__(self):
        return self.name


class Grains(db.Model):
    __tablename__ = 'host_grains'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), nullable=False)
    value = db.Column(db.String(64), nullable=False)
    host_id = db.Column(db.Integer, db.ForeignKey(Host.id))
    host = db.relationship(Host, backref=db.backref('grains', cascade="all, delete-orphan", single_parent=True))


class HostGroup(db.Model):
    __tablename__ = 'host_group'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.Text())


    def __unicode__(self):
        return self.name


class Returner(db.Model):
    __tablename__ = "jid"
    id = db.Column(db.Integer, primary_key=True)
    fun = db.Column(db.String(64))
    jid = db.Column(db.String(20), unique=True)

    @classmethod
    def all(cls):
        return Returner.query.order_by(db.desc(Returner.id)).all()

    @classmethod
    def write_ret(cls, ret):
        try:
            redis_cli.set('{0}:{1}'.format(ret['id'], ret['jid']), json.dumps(ret))
            redis_cli.lpush('{0}:{1}'.format(ret['id'], ret['fun']), ret['jid'])
        except Exception as ex:
            from app import app
            import traceback
            app.logger.warn(str(traceback.print_exc()))

    @classmethod
    def read_ret(cls, jid):
        try:
            keys = redis_cli.keys('*:{0}'.format(jid))
            ret = {}
            for k in keys:
                value = redis_cli.get(k)
                ret.setdefault(k, json.loads(value))
            return ret
        except Exception as ex:
            from app import app
            import traceback
            app.logger.warn(str(traceback.print_exc()))