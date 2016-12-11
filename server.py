#!/usr/bin/env python
# -*- coding: utf8 -*-

from tornado.ioloop import IOLoop
from application import application


if __name__ == '__main__':
    application.listen(8080)
    IOLoop.instance().start()

