#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Mail: tongdongdong@outlook.com
# Reference: https://cloud.tencent.com/document/product/302/8517
# QcloudApiv3 DNSPod 的 API 更新了 By github@z0z0r4

import json
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.dnspod.v20210323 import dnspod_client, models

class QcloudApiv3():
    def __init__(self, SECRETID, SECRETKEY):
        self.SecretId = SECRETID
        self.secretKey = SECRETKEY
        self.cred = credential.Credential(SECRETID, SECRETKEY)

    def del_record(self, domain: str, record_id: int):
        client = dnspod_client.DnspodClient(self.cred, "")
        req_model = models.DeleteRecordRequest()
        params = {
            "Domain": domain,
            "RecordId": record_id
        }
        req_model.from_json_string(json.dumps(params))


        resp = client.DeleteRecord(req_model)
        resp = json.loads(resp.to_json_string())
        resp["code"] = 0
        resp["message"] = "None"
        return resp

    def get_record(self, domain: str, length: int, sub_domain: str, record_type: str):
        def format_record(record: dict):
            new_record = {}
            record["id"] = record['RecordId']
            for key in record:
                new_record[key.lower()] = record[key]
            return new_record
        try:
            client = dnspod_client.DnspodClient(self.cred, "")
            
            req_model = models.DescribeRecordListRequest()
            params = {
                "Domain": domain,
                "Subdomain": sub_domain,
                "RecordType": record_type,
                "Limit": length
            }
            req_model.from_json_string(json.dumps(params))


            resp = client.DescribeRecordList(req_model)
            resp = json.loads(resp.to_json_string())
            temp_resp = {}
            temp_resp["code"] = 0
            temp_resp["data"] = {}
            temp_resp["data"]["records"] = []
            for record in resp['RecordList']:
                temp_resp["data"]["records"].append(format_record(record))
            temp_resp["data"]["domain"] = {}
            temp_resp["data"]["domain"]["grade"] = self.get_domain(domain)["DomainInfo"]["Grade"] # DP_Free
            return temp_resp
        except TencentCloudSDKException:
            # 构造空响应...
            temp_resp = {}
            temp_resp["code"] = 0
            temp_resp["data"] = {}
            temp_resp["data"]["records"] = []
            temp_resp["data"]["domain"] = {}
            temp_resp["data"]["domain"]["grade"] = self.get_domain(domain)["DomainInfo"]["Grade"] # DP_Free
            return temp_resp

    def create_record(self, domain: str, sub_domain: str, value: int, record_type: str = "A", line: str = "默认", ttl: int = 600):
        client = dnspod_client.DnspodClient(self.cred, "")
        req = models.CreateRecordRequest()
        params = {
            "Domain": domain,
            "SubDomain": sub_domain,
            "RecordType": record_type,
            "RecordLine": line,
            "Value": value,
            "ttl": ttl
        }
        req.from_json_string(json.dumps(params))

        # 返回的resp是一个CreateRecordResponse的实例，与请求对象对应
        resp = client.CreateRecord(req)
        resp = json.loads(resp.to_json_string())
        resp["code"] = 0
        resp["message"] = "None"
        return resp

    def change_record(self, domain: str, record_id: int, sub_domain: str, value: str, record_type: str = "A", line: str = "默认", ttl: int = 600):
        client = dnspod_client.DnspodClient(self.cred, "")
        req = models.ModifyRecordRequest()
        params = {
            "Domain": domain,
            "SubDomain": sub_domain,
            "RecordType": record_type,
            "RecordLine": line,
            "Value": value,
            "TTL": ttl,
            "RecordId": record_id
        }
        req.from_json_string(json.dumps(params))

        # 返回的resp是一个ChangeRecordResponse的实例，与请求对象对应
        resp = client.ModifyRecord(req)
        resp = json.loads(resp.to_json_string())
        resp["code"] = 0
        resp["message"] = "None"
        return resp

    def get_domain(self, domain: str):
        client = dnspod_client.DnspodClient(self.cred, "")

        # 实例化一个请求对象,每个接口都会对应一个request对象
        req = models.DescribeDomainRequest()
        params = {
            "Domain": domain
        }
        req.from_json_string(json.dumps(params))

        # 返回的resp是一个DescribeDomainResponse的实例，与请求对象对应
        resp = client.DescribeDomain(req)
        resp = json.loads(resp.to_json_string())
        return resp