#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import tornado.web
from urls import urls

settings = dict(
    templates_path=os.path.join(os.path.dirname(__file__), 'templates'),
    static_path=os.path.join(os.path.dirname(__file__), 'static'),
    debug=False,
)
application = tornado.web.Application(handlers=urls, **settings)