#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Mail: tongdongdong@outlook.com
# Reference: https://help.aliyun.com/document_detail/29776.html?spm=a2c4g.11186623.2.38.3fc33efexrOFkT
import json
from aliyunsdkcore import client
from aliyunsdkalidns.request.v20150109 import DescribeDomainRecordsRequest
from aliyunsdkalidns.request.v20150109 import DeleteDomainRecordRequest
from aliyunsdkalidns.request.v20150109 import UpdateDomainRecordRequest
from aliyunsdkalidns.request.v20150109 import AddDomainRecordRequest


rc_format = 'json'
class AliApi():
    def __init__(self, ACCESSID, SECRETKEY):
        self.access_key_id = ACCESSID
        self.access_key_secret = SECRETKEY

    def del_record(self, domain, record):
        clt = client.AcsClient(self.access_key_id, self.access_key_secret, 'cn-hangzhou')
        request = DeleteDomainRecordRequest.DeleteDomainRecordRequest()
        request.set_RecordId(record)
        request.set_accept_format(rc_format)
        result = clt.do_action(request).decode('utf-8')
        result = json.JSONDecoder().decode(result)
        return result

    def get_record(self, domain, length, sub_domain, record_type):
        clt = client.AcsClient(self.access_key_id, self.access_key_secret, 'cn-hangzhou')
        request = DescribeDomainRecordsRequest.DescribeDomainRecordsRequest()
        request.set_DomainName(domain)
        request.set_PageSize(length)
        request.set_RRKeyWord(sub_domain)
        request.set_Type(record_type)
        request.set_accept_format(rc_format)
        result = clt.do_action(request).decode('utf-8').replace('DomainRecords', 'data', 1).replace('Record', 'records', 1).replace('RecordId', 'id').replace('Value', 'value').replace('Line', 'line').replace('telecom', '电信').replace('unicom', '联通').replace('mobile', '移动').replace('oversea', '境外').replace('default', '默认')
        result = json.JSONDecoder().decode(result)
        return result

    def create_record(self, domain, sub_domain, value, record_type, line, ttl):
        clt = client.AcsClient(self.access_key_id, self.access_key_secret, 'cn-hangzhou')
        request = AddDomainRecordRequest.AddDomainRecordRequest()
        request.set_DomainName(domain)
        request.set_RR(sub_domain)
        if line == "电信":
            line = "telecom"
        elif line == "联通":
            line = "unicom"
        elif line == "移动":
            line = "mobile"
        elif line == "境外":
            line = "oversea"
        elif line == "默认":
            line = "default"
        request.set_Line(line)
        request.set_Type(record_type)
        request.set_Value(value)
        request.set_TTL(ttl)
        request.set_accept_format(rc_format)
        result = clt.do_action(request).decode('utf-8')
        result = json.JSONDecoder().decode(result)
        return result
        
    def change_record(self, domain, record_id, sub_domain, value, record_type, line, ttl):
        clt = client.AcsClient(self.access_key_id, self.access_key_secret, 'cn-hangzhou')
        request = UpdateDomainRecordRequest.UpdateDomainRecordRequest()
        request.set_RR(sub_domain)
        request.set_RecordId(record_id)
        if line == "电信":
            line = "telecom"
        elif line == "联通":
            line = "unicom"
        elif line == "移动":
            line = "mobile"
        elif line == "境外":
            line = "oversea"
        elif line == "默认":
            line = "default"
        request.set_Line(line)
        request.set_Type(record_type)
        request.set_Value(value)
        request.set_TTL(ttl)
        request.set_accept_format(rc_format)
        result = clt.do_action(request).decode('utf-8')
        result = json.JSONDecoder().decode(result)
        return result

