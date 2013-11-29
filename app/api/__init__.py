#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#  tanyewei@gmail.com
#  2013/11/28 18:50
import salt.client.api
from salt.exceptions import EauthAuthenticationError


def tokenify(cmd, token=None):
    if token is not None:
        cmd['token'] = token
    return cmd


def create_token(creds):
    '''
        creds = dict(
            username=username,
            password=password,
            eauth=eauth,
        )
    '''
    client = salt.client.api.APIClient()
    try:
        creds = client.create_token(creds)
        return creds
    except:
        return None


def run(token='4907610066c43ebe2d3f32c0c73e92a0'):
    cmds = [{"fun": "cmd.run", "mode": "async", "tgt": "test1", "arg": ["uptime"], "expr_form": "compound"}]
    client = salt.client.api.APIClient()
    try:
        results = [client.run(tokenify(cmd, token)) for cmd in cmds]
        return results
    except:
        pass