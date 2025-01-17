import oss2
import base64
import os
import urllib.parse as urllib

from django.conf import settings

from common.core.str_helper import StrHelper
from common.core.time_helper import timer


class OSSHelper(object):
    def __init__(self):
        super(OSSHelper, self).__init__()
        self.access_key_id = settings.OSS_ACCESS_KEY_ID
        self.access_key_secret = settings.OSS_ACCESS_KEY_SECRET
        self.endpoint = settings.OSS_ENDPOINT
        self.host = settings.OSS_HOST
        self.bucket = settings.OSS_BUCKET
        self.valid_time = settings.OSS_VALID_TIME

    @staticmethod
    def get_decoded_file(file):
        file_suffix, file = file.split(',')
        # _, data_format = file_suffix.split(';')[0].split('/')
        file = base64.decodebytes(file.encode('utf8'))
        return file

    @staticmethod
    def get_data_format(file):
        file_suffix, file = file.split(',')
        _, data_format = file_suffix.split(';')[0].split('/')
        return data_format

    def upload_file(self, object_name, file, is_stream=False):
        auth = oss2.Auth(self.access_key_id, self.access_key_secret)
        bucket = oss2.Bucket(auth, self.endpoint, self.bucket)
        if is_stream:
            bucket.put_object(object_name, file.iter_content(chunk_size=8192))
        else:
            bucket.put_object(object_name, file)
        return

    def update_object_meta(self, object_name, file_name, use_attachment=True):
        auth = oss2.Auth(self.access_key_id, self.access_key_secret)
        bucket = oss2.Bucket(auth, self.endpoint, self.bucket)
        file_name = urllib.parse.quote_plus(file_name)
        if use_attachment:
            disposition_type = 'attachment'
            headers = {
                'content-disposition': "{0};filename={1};filename*=UTF-8''{1}".format(disposition_type, file_name)
            }
        else:
            headers = {'content-disposition': "filename={0};filename*=UTF-8''{0}".format(file_name)}
        bucket.update_object_meta(object_name, headers)

    @timer
    def get_file_url(self, object_name, valid_time=None):
        if not object_name:
            return
        auth = oss2.Auth(self.access_key_id, self.access_key_secret)
        bucket = oss2.Bucket(auth, self.endpoint, self.bucket)
        if valid_time is None:
            valid_time = self.valid_time
        file_url = bucket.sign_url('GET', object_name, valid_time)
        file_url = file_url.replace("http://", "https://")
        # file_url = urllib.unquote(file_url)
        return file_url

    @timer
    def get_thumbnail_url(self, object_name, valid_time=None, size='w_100,h_100'):
        if not object_name:
            return
        auth = oss2.Auth(self.access_key_id, self.access_key_secret)
        bucket = oss2.Bucket(auth, self.endpoint, self.bucket)
        if valid_time is None:
            valid_time = self.valid_time

        style = f'image/resize,m_fixed,{size}'
        url = bucket.sign_url('GET', object_name, valid_time, params={'x-oss-process': style})
        url = url.replace("http://", "https://")
        return url

    @timer
    def get_file_size(self, object_name):
        if not object_name:
            return
        auth = oss2.Auth(self.access_key_id, self.access_key_secret)
        bucket = oss2.Bucket(auth, self.endpoint, self.bucket)
        head_result = bucket.head_object(object_name)
        size = head_result.content_length
        return size

    def get_file(self, object_name):
        if not object_name:
            return
        auth = oss2.Auth(self.access_key_id, self.access_key_secret)
        bucket = oss2.Bucket(auth, self.endpoint, self.bucket)
        file = bucket.get_object(object_name)
        content = file.read()
        return content

    def delete_file(self, object_name):
        auth = oss2.Auth(self.access_key_id, self.access_key_secret)
        bucket = oss2.Bucket(auth, self.endpoint, self.bucket)
        bucket.delete_object(object_name)
        return

    def get_key_added_data(self, request_data, pk, prefix, is_b64_data=True, is_stream=False, use_slash=True, use_attachment=False):
        key = self.get_key_name(request_data, pk, prefix, use_slash)
        request_data['key'] = key
        if is_b64_data:
            file = self.get_decoded_file(request_data['data'])
        else:
            file = request_data['data']
        self.upload_file(object_name=key, file=file, is_stream=is_stream)
        self.update_object_meta(object_name=key, file_name=request_data['fileName'], use_attachment=use_attachment)
        return request_data

    def get_key_name(self, request_data, pk, prefix, use_slash=True):
        filename = request_data['fileName'] or ''
        assert filename != '', 'fileName是必填项。'
        if use_slash:
            key = os.path.join(prefix, pk + '/', filename)
        else:
            key = StrHelper.get_file_key_by_name(filename)
            key = os.path.join(prefix, key)
        return key

    def copy_file(self, source_key, target_key):
        auth = oss2.Auth(self.access_key_id, self.access_key_secret)
        bucket = oss2.Bucket(auth, self.endpoint, self.bucket)
        bucket.copy_object(self.bucket, source_key, target_key)
        return

    def get_bucket_instance(self):
        auth = oss2.Auth(self.access_key_id, self.access_key_secret)
        bucket = oss2.Bucket(auth, self.endpoint, self.bucket)
        return bucket