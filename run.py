#!/usr/bin/env python
# -*- coding: utf-8 -*- 
#  tanyewei@gmail.com
#  2013/11/26 14:15
from app import app, ctx

if __name__ == "__main__":
    import logging

    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(host='0.0.0.0', debug=True, ssl_context=ctx)