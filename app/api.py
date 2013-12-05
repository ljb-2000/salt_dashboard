#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#  tanyewei@gmail.com
#  2013/12/05 10:55
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

