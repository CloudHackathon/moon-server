#!/usr/bin/env python
# -*- coding: utf8 -*-
import time
import json
import logging
import requests
from collections import Counter
from qcloud_cos import CosClient, Auth, UploadFileRequest
from constants import *

youtu_log = logging.getLogger(__name__)

KNOWN = 'known'
UNKNOWN = 'unknown'


class YoutuException(BaseException):

    pass


class YoutuManager(object):

    def __init__(self, host, app_id, secret_id, secret_key, region, bucket):
        self.cos_client = CosClient(int(app_id), secret_id, secret_key, region)
        self._bucket = unicode(bucket)
        self._host = host

    def _url(self, path):
        return "http://" + self._host + path

    def _sign(self):
        return Auth(self.cos_client.get_cred()).sign_more(
            self._bucket, '', int(time.time()) + 30
        )

    def _params(self, **kwargs):
        kwargs['appid'] = str(self.cos_client.get_cred().get_appid())
        kwargs['bucket'] = self._bucket
        return kwargs

    def _upload_picture(self, local_path):
        image_name = local_path.split('/')[-1]
        remote_path = "/face/" + image_name
        request = UploadFileRequest(self._bucket, unicode(remote_path), unicode(local_path), insert_only=0)
        try:
            result = self.cos_client.upload_file(request)
        except Exception, e:
            raise YoutuException("update file %s failed, %s" % (image_name, e))
            return None
        else:
            youtu_log.debug("upload_file result:%s" % result)
            source_url = result['data']['source_url']
            return source_url

    def _post(self, url, params):
        headers = {
            'Host': self._host,
            'Content-Type': 'application/json',
            'Authorization': self._sign()
        }
        json_data = json.dumps(params)
        try:
            response = requests.post(url, data=json_data, headers=headers)
        except Exception, e:
            raise YoutuException(
                "http post error url=%s, data=%s, headers=%s. original error: %s" % (
                    url, json_data, headers, e
                ))
        else:
            return json.loads(response.text)

    def create_person(self, image_url, person_id, group_id, person_name="", tag=""):
        url = self._url('/face/newperson')
        params = self._params(
            url=image_url, group_ids=[group_id], person_id=str(person_id), person_name=person_name, tag=tag
        )
        print params
        response_data = self._post(url, params)
        print response_data
        if response_data['code'] != 0:
            raise YoutuException("create person failed, " + response_data['message'])
        return response_data['data']['person_id']

    def add_face(self, image_url, person_id, tag=""):
        url = self._url('/face/addface')
        params = self._params(
            person_id=person_id,
            urls=[image_url],
            tag=tag
        )
        response_data = self._post(url, params)
        print response_data
        if response_data['code'] != 0:
            raise YoutuException("add face to person %s failed, " % person_id + response_data['message'])
        return person_id

    def set_person_info(self, person_id, person_name):
        url = self._url("/face/setinfo")
        params = self._params(
            person_id=person_id,
            person_name=person_name
        )
        response_data = self._post(url, params)
        if response_data['code'] != 0:
            raise YoutuException("set person %s info failed, " % person_id + response_data['message'])
        return response_data['data']['person_id']

    def get_person_info(self, person_id):
        url = self._url("/face/getinfo")
        params = self._params(person_id=person_id)
        response_data = self._post(url, params)
        if response_data['code'] != 0:
            raise YoutuException("get person %s info failed, " % person_id + response_data['message'])
        return response_data['data']

    def get_face_info(self, face_id):
        url = self._url("/face/getfaceinfo")
        params = self._params(face_id=face_id)
        response_data = self._post(url, params)
        if response_data['code'] != 0:
            raise YoutuException("get face %s info failed, " % face_id + response_data['message'])
        return response_data['data']

    def face_detect(self, image_url):
        url = self._url("/face/detect")
        params = self._params(url=image_url, mode=1)
        response_data = self._post(url, params)
        return response_data

    def face_identify(self, image_url, group_id):
        url = self._url("/face/identify")
        params = self._params(group_id=group_id, url=image_url)
        response_data = self._post(url, params)
        print response_data
        if response_data['code'] != 0:
            raise YoutuException("face %s identify %s  failed, " % (image_url, group_id) + response_data['message'])
        return response_data['data']['candidates']

    def face_detect_upload(self, local_path):
        image_url = self._upload_picture(local_path)
        response = self.face_detect(image_url)
        if response['code'] == 0: pass
        return image_url

    def face_identify_one(self, image_url):
        candidates = self.face_identify(image_url, "known") + self.face_identify(image_url, "unknown")
        candidate = {}
        for c in candidates:
            if c['confidence'] > 60 and c['confidence'] > candidate.get('confidence', 0):
                candidate = c
        return candidate




python




