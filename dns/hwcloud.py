#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: ravizhan
# Github: https://github.com/ravizhan
# Mail: ravizhan@hotmail.com
# Reference: https://apiexplorer.developer.huaweicloud.com/apiexplorer/doc?product=DNS
import json
import requests
import signer


# 所有函数请求成功会返回success或相关数据，失败则会返回接口返回的原始数据
# 所有参数值均限定数据类型
class Hwcloud:
    # 定义AK，SK，实例化鉴权SDK
    # AK SK生成: https://support.huaweicloud.com/devg-apisign/api-sign-provide-aksk.html
    def __init__(self, AK, SK):
        self.sign = signer.Signer()
        self.sign.Key = AK
        self.sign.Secret = SK

    # 获取域名的zone_id，供其他函数调用
    def get_zone_id(self, domain: str):
        url = 'https://dns.myhuaweicloud.com/v2/zones?type=public'
        r = signer.HttpRequest('GET', url)
        self.sign.Sign(r)
        res = json.loads(requests.get(url, headers=r.headers).text)
        # print(res)
        zone_id = ''
        for i in range(0, len(res['zones'])):
            if domain == res['zones'][i]['name'][:-1]:
                zone_id = res['zones'][i]['id']
        if zone_id != '':
            return zone_id
        else:
            return "The domain doesn't exist"

    # 删除解析记录，domain为主域名，record为解析记录的id，该id可用get_record函数取得.
    def del_record(self, domain: str, record: str):
        zone_id = self.get_zone_id(domain)
        if zone_id != "The domain doesn't exist":
            url = 'https://dns.myhuaweicloud.com/v2/zones/' + zone_id + '/recordsets/' + record
        else:
            return "The domain doesn't exist"
        r = signer.HttpRequest('DELETE', url)
        self.sign.Sign(r)
        res = json.loads(requests.delete(url, headers=r.headers).text)
        # print(res['status'])
        try:
            if res['status'] == 'PENDING_DELETE':
                return 'success'
        except:
            return res

    # 获取解析记录的id，domain为主域名，length为请求列表的长度，sub_domain为子域名，只取前缀即可，record_type为解析类型
    def get_record(self, domain: str, length: int, sub_domain: str, record_type: str):
        zone_id = self.get_zone_id(domain)
        if zone_id != "The domain doesn't exist":
            url = 'https://dns.myhuaweicloud.com/v2.1/zones/' + zone_id + '/recordsets?limit=' + str(length)
        else:
            return "The domain doesn't exist"
        r = signer.HttpRequest('GET', url)
        self.sign.Sign(r)
        res = json.loads(requests.get(url, headers=r.headers).text)
        records = []
        recordset_id = ''
        # print(res)
        try:
            for i in range(0, len(res['recordsets'])):
                if res['recordsets'][i]['name'].split('.')[0] == sub_domain and res['recordsets'][i]['type'] == record_type:
                    records = res['recordsets'][i]['records']
                    recordset_id = res['recordsets'][i]['id']
            if records and recordset_id != '':
                return records, recordset_id
            else:
                return "The sub domain doesn't exist"
        except:
            return res

    # 创建解析记录，domain为主域名，sub_domain为子域名，value为记录值，可以列表形式传入多个值,line为线路，为了适配，传入电信/联通/移动即可
    # ttl为生效时间，华为云不限制ttl，默认为300s，最小可1s
    def create_record(self, domain: str, sub_domain: str, value: list, record_type: str, line: str, ttl: int):
        zone_id = self.get_zone_id(domain)
        if zone_id != "The domain doesn't exist":
            url = 'https://dns.myhuaweicloud.com/v2.1/zones/' + zone_id + '/recordsets'
        else:
            return "The domain doesn't exist"
        if line == '电信':
            line = 'Dianxin'
        elif line == '联通':
            line = 'Liantong'
        elif line == '移动':
            line = 'Yidong'
        ips = []
        ips.append(value)
        data = {
            "line": line,
            "name": sub_domain + '.' + domain,
            "records": value,
            "ttl": ttl,
            "type": record_type
        }
        r = signer.HttpRequest('POST', url, body=json.dumps(data))
        self.sign.Sign(r)
        res = json.loads(requests.post(url, headers=r.headers, data=r.body).text)
        # print(res)
        # print(res['status'])
        try:
            if res['status'] == 'PENDING_CREATE':
                return 'success'
        except:
            return res

    # 更改解析记录，domain为主域名，record为解析记录的id，该id可用get_record函数取得，value为记录值，ttl为生效时间。
    def change_record(self, domain: str, record_id: str, value: str, ttl: int):
        zone_id = self.get_zone_id(domain)
        if zone_id != "The domain doesn't exist":
            url = 'https://dns.myhuaweicloud.com/v2.1/zones/' + zone_id + '/recordsets/' + record_id
        else:
            return "The domain doesn't exist"
        data = {
            "records": [
                value
            ],
            "ttl": ttl,
        }
        r = signer.HttpRequest('PUT', url, body=json.dumps(data))
        self.sign.Sign(r)
        res = json.loads(requests.put(url, headers=r.headers, data=r.body).text)
        # print(res)
        try:
            if res['status'] == 'PENDING_UPDATE' or res['status'] == 'ACTIVE':
                return 'success'
        except:
            return res


if __name__ == '__main__':
    AK = ''
    SK = ''
    api = Hwcloud(AK, SK)
    # 一些demo
    # print(api.get_zone_id('ravizhan.top'))
    # print(api.get_record('ravizhan.top',20,'abc','A'))
    # print(api.del_record('ravizhan.top','8aace3ba763e2fd50177a570199f5ffe'))
    # print(api.create_record('ravizhan.top','abc','1.1.1.1','A','联通',1))
    # print(api.change_record('ravizhan.top','8aace3b9763e2fc70177a98e37357976','1.2.3.4',10))
