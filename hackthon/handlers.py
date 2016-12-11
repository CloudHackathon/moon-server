#!/usr/bin/env python
# -*- coding: utf8 -*-
import os
import json
from tornado.web import RequestHandler
from models import session_factory, Record
from utils import base64_to_image
from youtu import YoutuManager
from constants import *


class BaseHandler(RequestHandler):

    files_path = os.path.abspath("./files")

    def initialize(self):
        self.session = session_factory()
        self.youtu = YoutuManager(HOST, APP_ID, SECRET_ID, SECRET_KEY, REGION, BUCKET)
        self.set_header("Content-Type", "application/json")

    def response(self, code, message, person_id):
        r = dict(code=code, message=message, person_id=person_id)
        return json.dumps(r)

    def on_finish(self):
        self.session.close()


class HelloHandler(RequestHandler):

    def get(self):
        return self.write("Hello my friend")

    def post(self):
        image_base64 = self.get_argument("image")
        print image_base64
        print base64_to_image(image_base64)
        return self.write("success")


class PhotoUpload(BaseHandler):

    def post(self):
        print "-------"
        image_url = self.image_detect()
        if not image_url:
            return self.write(self.response(3, "face detect failed", {}))
        is_known = self.get_argument("is_known")
        if is_known == "yes":
            person_id = self.known(image_url)
            return self.write(
                self.response(0, "register person success", {"person_id": person_id, "image_url": r.image_url})
            )
        else:
            candidate, record = self.unknown(image_url)
            if not candidate:
                person_id = record.person_id
                self.youtu.create_person(image_url, person_id, "unknown")
                return self.write(
                    self.response(1, "identify person failed, register unknown person",
                                  {"person_id": person_id, "image_url": image_url}))
            else:
                self.youtu.add_face(image_url, candidate["person_id"])
                r = self.session.query(Record).filter_by(person_id=candidate["person_id"])
                return self.write(self.response(2, "identify person success, add face to person",
                                  {"person_id": candidate['person_id'], "image_url": r.image_url, "name": name}))

    def image_detect(self):
        image = self.get_argument("image")
        image_name, image_data = base64_to_image(image)
        local_image_path = os.path.join(self.files_path, image_name)
        with open(local_image_path, "wb") as f:
            f.write(image_data)
        image_url = self.youtu.face_detect_upload(local_image_path)
        return image_url

    def known(self, image_url):
        id_no = self.get_argument("idNo")
        name = self.get_argument("name")
        remark = self.get_argument("remark")
        record = Record(image_url=image_url, name=name, remark=remark)
        self.session.add(record)
        self.session.commit()
        person_id = self.youtu.create_person(image_url, record.person_id, "known", name)
        return person_id

    def unknown(self, image_url):
        longitude = self.get_argument("longitude")
        latitude = self.get_argument("latitude")
        timestamp = self.get_argument("timestamp")
        record = Record(image_url=image_url, longitude=longitude, latitude=latitude, timestamp=timestamp)
        self.session.add(record)
        self.session.commit()
        candidate = self.youtu.face_identify_one(image_url)
        return candidate, record






