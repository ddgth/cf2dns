#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Mail: tongdongdong@outlook.com
# Reference: https://cloud.tencent.com/document/product/302/8517
import base64
import hashlib
import hmac
import random
import time
import operator
import json
import urllib.parse
import urllib3

class QcloudApi():
    def __init__(self, SECRETID, SECRETKEY):
        self.SecretId = SECRETID
        self.secretKey = SECRETKEY

    def get(self, module, action, **params):
        config = {
            'Action': action,
            'Nonce': random.randint(10000, 99999),
            'SecretId': self.SecretId,
            'SignatureMethod': 'HmacSHA256',
            'Timestamp': int(time.time()),
        }
        url_base = '{0}.api.qcloud.com/v2/index.php?'.format(module)

        params_all = dict(config, **params)

        params_sorted = sorted(params_all.items(), key=operator.itemgetter(0))

        srcStr = 'GET{0}'.format(url_base) + ''.join("%s=%s&" % (k, v) for k, v in dict(params_sorted).items())[:-1]
        signStr = base64.b64encode(hmac.new(bytes(self.secretKey, encoding='utf-8'), bytes(srcStr, encoding='utf-8'), digestmod=hashlib.sha256).digest()).decode('utf-8')

        config['Signature'] = signStr

        params_last = dict(config, **params)

        params_url = urllib.parse.urlencode(params_last)

        url = 'https://{0}&'.format(url_base) + params_url
        http = urllib3.PoolManager()
        r = http.request('GET', url=url, retries=False)
        ret = json.loads(r.data.decode('utf-8'))
        if ret.get('code', {}) == 0:
            return ret
        else:
            raise Exception(ret)

    def del_record(self, domain, record):
        return self.get(module = 'cns', action = 'RecordDelete', domain = domain, recordId = record)

    def get_record(self, domain, length, sub_domain, record_type):
        return self.get(module = 'cns', action = 'RecordList', domain = domain, length = length, subDomain = sub_domain, recordType = record_type)

    def create_record(self, domain, sub_domain, value, record_type, line, ttl):
        return self.get(module = 'cns', action = 'RecordCreate', domain = domain, subDomain = sub_domain, value = value, recordType = record_type, recordLine = line, ttl = ttl)

    def change_record(self, domain, record_id, sub_domain, value, record_type, line, ttl):
        return self.get(module = 'cns', action = 'RecordModify', domain = domain, recordId =record_id, subDomain = sub_domain, value = value, recordType = record_type, recordLine = line, ttl = ttl)