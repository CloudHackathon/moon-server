#!/usr/bin/env python
# -*- coding: utf8 -*-

from hackthon.handlers import HelloHandler, PhotoUpload

urls = [
    (r'/hello', HelloHandler),
    (r'/upload', PhotoUpload),
]