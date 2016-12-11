#!/usr/bin/env python
# -*- coding: utf8 -*-

import requests
import json
import traceback
import time
from qcloud_cos import UploadFileRequest, CosClient, Auth

APP_ID = '1251284294'
SECRET_ID = u'AKID7Tyt7jUoyrEAWYr8h2KEISPgDRNRtp3m'
SECRET_KEY = u'VQrxUzaabFFsq1lvvE8qZnkCILIDVakh'
REGION = "guangzhou"
BUCKET = "hackthon"
FACE_COMPARE_THRESHOLD = 60


class YouTu(object):

    host = 'service.image.myqcloud.com'

    def __init__(self, app_id, secret_id, secret_key, region, bucket):
        self.bucket = unicode(bucket)
        self.cos_client = CosClient(int(app_id), secret_id, secret_key, region)
        self.auth = Auth(self.cos_client.get_cred())

    def _assemble_url(self, path):
        return 'http://%s%s' % (self.host, path)

    def _get_sign(self):
        return self.auth.sign_more(self.bucket, '', int(time.time()+30))

    def upload_picture(self, local, remote):
        request = UploadFileRequest(self.bucket, unicode(remote), unicode(local), insert_only=0)
        result = self.cos_client.upload_file(request)
        data = result.get('data', None)
        if data:
            return data.get('source_url', None)
        else:
            return None

    def face_detect(self, picture_url):
        url = self._assemble_url('/face/detect')
        sign = self._get_sign()
        headers = {
            'Host': 'service.image.myqcloud.com',
            'Content-Type': 'application/json',
            'Authorization': sign
        }
        data = {
            "appid": str(self.cos_client.get_cred().get_appid()),
            "bucket": self.bucket,
            "mode": 1,
            "url": picture_url
        }
        response = requests.post(url, data=json.dumps(data), headers=headers)
        response_data = json.loads(response.text)
        if response_data.get('code', None) == 0:
            data = response_data.get('data')
            face = data.get('face')[0]
            age = face.get('age')
            gender = face.get('gender')
            sex = 0 if gender < 50 else 1
            return {'sex': sex, 'age': age}
        else:
            print data
            return None

    def face_compare(self, picture_url, another_picture_url):
        url = self._assemble_url('/face/compare')
        sign = self._get_sign()
        headers = {
            'Host': 'service.image.myqcloud.com',
            'Content-Type': 'application/json',
            'Authorization': sign
        }
        data = {
            "appid": str(self.cos_client.get_cred().get_appid()),
            "bucket": self.bucket,
            "urlA": picture_url,
            "urlB": another_picture_url,
        }
        response = requests.post(url, data=json.dumps(data), headers=headers)
        response_data = json.loads(response.text)
        score = response_data['data']['similarity']
        return score


"""youtu = YouTu(APP_ID, SECRET_ID, SECRET_KEY, REGION, 'hackthon')
js1_url = youtu.upload_picture('/Users/sean/Documents/js1.jpeg', '/temp/js1.jpeg')
js2_url = youtu.upload_picture('/Users/sean/Documents/js2.jpeg', '/temp/js2.jpeg')
tank_url = youtu.upload_picture('/Users/sean/Documents/tank.jpeg', '/temp/tank.jpeg')
youtu.face_detect(tank_url)
youtu.face_detect(js1_url)
youtu.face_detect(js2_url)
print youtu.face_compare(js1_url, js2_url)
print youtu.face_compare(js1_url, tank_url)"""