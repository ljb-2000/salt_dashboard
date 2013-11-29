#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#  tanyewei@gmail.com
#  2013/11/26 14:54
from app import db
class Host(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.Text())
    public_ip = db.Column(db.String(64))
    public_ip_secondary = db.Column(db.String(64))
    private_ip = db.Column(db.String(64))
    group_id = db.Column(db.Integer, db.ForeignKey('host_group.id'))
    saltversion = db.Column(db.String(64), default='0')
    grains = db.Column(db.String(128))
    group = db.relationship('HostGroup', backref='groups')


    def __unicode__(self):
        return self.name


class HostGroup(db.Model):
    __tablename__ = 'host_group'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.Text())


    def __unicode__(self):
        return self.name