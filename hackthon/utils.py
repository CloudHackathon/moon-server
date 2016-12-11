#!/usr/bin/env python
# -*- coding: utf8 -*-
import os
import base64
import hashlib


def base64_to_image(base64_str):
    image_data = base64.b64decode(base64_str)
    image_md5 = hashlib.md5(image_data)
    image_name = image_md5.hexdigest() + ".jpg"
    return image_name, image_data

