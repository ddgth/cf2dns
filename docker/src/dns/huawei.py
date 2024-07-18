#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author/Mail: tongdongdong@outlook.com
# Reference1: https://github.com/huaweicloud/huaweicloud-sdk-python-v3/tree/ff7df92d2a496871c7c2d84dfd2a7f4e2467fff5/huaweicloud-sdk-dns/huaweicloudsdkdns/v2/model 
# Reference2: https://support.huaweicloud.com/api-dns/dns_api_65003.html
# REGION: https://developer.huaweicloud.com/endpoint

from re import sub
from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkdns.v2 import *
from huaweicloudsdkdns.v2.region.dns_region import DnsRegion
import json


class HuaWeiApi():
    def __init__(self, ACCESSID, SECRETKEY, REGION = 'cn-east-3'):
        self.AK = ACCESSID
        self.SK = SECRETKEY
        self.region = REGION
        self.client = DnsClient.new_builder().with_credentials(BasicCredentials(self.AK, self.SK)).with_region(DnsRegion.value_of(self.region)).build()
        self.zone_id = self.get_zones()

    def del_record(self, domain, record):
        request = DeleteRecordSetsRequest()
        request.zone_id = self.zone_id[domain + '.']
        request.recordset_id = record
        response = self.client.delete_record_sets(request)
        result = json.loads(str(response))
        print(result)
        return result

    def get_record(self, domain, length, sub_domain, record_type):
        request = ListRecordSetsWithLineRequest()
        request.limit = length
        request.type = record_type
        if sub_domain == '@':
            request.name = domain + "."
        else:
            request.name = sub_domain + '.' + domain + "."
        response = self.client.list_record_sets_with_line(request)
        data = json.loads(str(response))
        result = {}
        records_temp = []
        for record in data['recordsets']:
            if (sub_domain == '@' and domain + "." == record['name']) or (sub_domain + '.' + domain + "." == record['name']):
                record['line'] = self.line_format(record['line'])
                record['value'] = '1.1.1.1'
                records_temp.append(record)
        result['data'] = {'records': records_temp}
        return result

    def create_record(self, domain, sub_domain, value, record_type, line, ttl):
        request = CreateRecordSetWithLineRequest()
        request.zone_id = self.zone_id[domain + '.']
        if sub_domain == '@':
            name = domain + "."
        else:
            name = sub_domain + '.' + domain + "."
        request.body = CreateRecordSetWithLineReq(
            type = record_type,
            name = name,
            ttl = ttl,
            weight = 1,
            records = [value],
            line = self.line_format(line)
        )
        response = self.client.create_record_set_with_line(request)
        result = json.loads(str(response))
        return result
        
    def change_record(self, domain, record_id, sub_domain, value, record_type, line, ttl):
        request = UpdateRecordSetRequest()
        request.zone_id = self.zone_id[domain + '.']
        request.recordset_id = record_id
        if sub_domain == '@':
            name = domain + "."
        else:
            name = sub_domain + '.' + domain + "."
        request.body = UpdateRecordSetReq(
            name = name,
            type = record_type,
            ttl = ttl,
            records=[value]
        )
        response = self.client.update_record_set(request)
        result = json.loads(str(response))
        return result

    def get_zones(self):
        request = ListPublicZonesRequest()
        response = self.client.list_public_zones(request)
        result = json.loads(str(response))
        zone_id = {}
        for zone in result['zones']:
            zone_id[zone['name']] = zone['id'] 
        return zone_id

    def line_format(self, line):
        lines = {
            '默认' : 'default_view',
            '电信' : 'Dianxin',
            '联通' : 'Liantong',
            '移动' : 'Yidong',
            '境外' : 'Abroad',
            'default_view' : '默认',
            'Dianxin' : '电信',
            'Liantong' : '联通',
            'Yidong' : '移动',
            'Abroad' : '境外',
        }
        return lines.get(line, None)

if __name__ == '__main__':
    hw_api = HuaWeiApi('WTTCWxxxxxxxxx84O0V', 'GXkG6D4X1Nxxxxxxxxxxxxxxxxxxxxx4lRg6lT')
    print(hw_api.get_record('xxxx.com', 100, '@', 'A'))
