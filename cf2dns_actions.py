#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Mail: tongdongdong@outlook.com
import base64
import hashlib
import hmac
import random
import time
import operator
import json
import urllib.parse
import urllib3
import os

#可以从https://shop.hostmonit.com获取
KEY = os.environ["KEY"]  #"o1zrmHAF"
#CM:移动 CU:联通 CT:电信
#修改需要更改的dnspod域名核子域名
DOMAINS = json.loads(os.environ["DOMAINS"])  #{"hostmonit.com": {"@": ["CM","CU","CT"], "shop": ["CM", "CU", "CT"], "stock": ["CM","CU","CT"]},"4096.me": {"@": ["CM","CU","CT"], "vv": ["CM","CU","CT"]}}
#腾讯云后台获取 https://console.cloud.tencent.com/cam/capi
SECRETID = os.environ["SECRETID"]    #'AKIDV**********Hfo8CzfjgN'
SECRETKEY = os.environ["SECRETKEY"]   #'ZrVs*************gqjOp1zVl'
#默认为普通版本 不用修改
AFFECT_NUM = 2


urllib3.disable_warnings()
class QcloudApi():
    def __init__(self):
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


def get_optimization_ip():
    try:
        http = urllib3.PoolManager()
        headers = headers = {'Content-Type': 'application/json'}
        data = {"key": KEY}
        data = json.dumps(data).encode()
        response = http.request('POST','https://api.hostmonit.com/get_optimization_ip',body=data, headers=headers)
        return json.loads(response.data.decode('utf-8'))
    except Exception as e:
        print(e)
        return None

def changeDNS(line, s_info, c_info, domain, sub_domain, qcloud):
    global AFFECT_NUM
    if line == "CM":
        line = "移动"
    elif line == "CU":
        line = "联通"
    elif line == "CT":
        line = "电信"
    else:
        print("CHANGE DNS ERROR: ----Time: " + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "----MESSAGE: LINE ERROR")
        return
    try:
        create_num = AFFECT_NUM - len(s_info)
        if create_num == 0:
            for info in s_info:
                if len(c_info) == 0:
                    break
                cf_ip = c_info.pop(0)["ip"]
                if cf_ip in str(s_info):
                    continue
                ret = qcloud.get(module='cns', action='RecordModify', domain=domain, recordId=info["recordId"], subDomain=sub_domain, value=cf_ip, recordType='A', recordLine=line)
                if(ret["code"] == 0):
                    print("CHANGE DNS SUCCESS: ----Time: " + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "----DOMAIN: " + domain + "----SUBDOMAIN: " + sub_domain + "----RECORDLINE: "+line+"----RECORDID: " + str(info["recordId"]) + "----VALUE: " + cf_ip )
                else:
                    print("CHANGE DNS ERROR: ----Time: " + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "----DOMAIN: " + domain + "----SUBDOMAIN: " + sub_domain + "----RECORDLINE: "+line+"----RECORDID: " + str(info["recordId"]) + "----VALUE: " + cf_ip + "----MESSAGE: " + ret["message"] )
        elif create_num > 0:
            for i in range(create_num):
                if len(c_info) == 0:
                    break
                cf_ip = c_info.pop(0)["ip"]
                if cf_ip in str(s_info):
                    continue
                ret = qcloud.get(module='cns', action='RecordCreate', domain=domain, subDomain=sub_domain, value=cf_ip, recordType='A', recordLine=line)
                if(ret["code"] == 0):
                    print("CREATE DNS SUCCESS: ----Time: " + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "----DOMAIN: " + domain + "----SUBDOMAIN: " + sub_domain + "----RECORDLINE: "+line+"----VALUE: " + cf_ip )
                else:
                    print("CHANGE DNS ERROR: ----Time: " + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "----DOMAIN: " + domain + "----SUBDOMAIN: " + sub_domain + "----RECORDLINE: "+line+"----RECORDID: " + str(info["recordId"]) + "----VALUE: " + cf_ip + "----MESSAGE: " + ret["message"] )
        else:
            for info in s_info:
                if create_num == 0 or len(c_info) == 0:
                    break
                cf_ip = c_info.pop(0)["ip"]
                if cf_ip in str(s_info):
                    create_num += 1
                    continue
                ret = qcloud.get(module='cns', action='RecordModify', domain=domain, recordId=info["recordId"], subDomain=sub_domain, value=cf_ip, recordType='A', recordLine=line)
                if(ret["code"] == 0):
                    print("CHANGE DNS SUCCESS: ----Time: " + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "----DOMAIN: " + domain + "----SUBDOMAIN: " + sub_domain + "----RECORDLINE: "+line+"----RECORDID: " + str(info["recordId"]) + "----VALUE: " + cf_ip )
                else:
                    print("CHANGE DNS ERROR: ----Time: " + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "----DOMAIN: " + domain + "----SUBDOMAIN: " + sub_domain + "----RECORDLINE: "+line+"----RECORDID: " + str(info["recordId"]) + "----VALUE: " + cf_ip + "----MESSAGE: " + ret["message"] )
                create_num += 1
    except Exception as e:
            print("CHANGE DNS ERROR: ----Time: " + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "----MESSAGE: " + str(e))

def main(qcloud):
    global AFFECT_NUM
    if len(DOMAINS) > 0:
        try:
            cfips = get_optimization_ip()
            if cfips == None or cfips["code"] != 200:
                print("GET CLOUDFLARE IP ERROR: ----Time: " + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "----MESSAGE: " + str(cfips["info"]))
                return
            cf_cmips = cfips["info"]["CM"]
            cf_cuips = cfips["info"]["CU"]
            cf_ctips = cfips["info"]["CT"]
            for domain, sub_domains in DOMAINS.items():
                for sub_domain, lines in sub_domains.items():
                    temp_cf_cmips = cf_cmips.copy()
                    temp_cf_cuips = cf_cuips.copy()
                    temp_cf_ctips = cf_ctips.copy()
                    ret = qcloud.get(module='cns', action='RecordList', domain=domain, length=100, subDomain=sub_domain, recordType="A")
                    if ret["code"] == 0:
                        if "Free" in ret["data"]["domain"]["grade"] and AFFECT_NUM > 2:
                            AFFECT_NUM = 2
                        cm_info = []
                        cu_info = []
                        ct_info = []
                        for record in ret["data"]["records"]:
                            if record["line"] == "移动":
                                info = {}
                                info["recordId"] = record["id"]
                                info["value"] = record["value"]
                                cm_info.append(info)
                            if record["line"] == "联通":
                                info = {}
                                info["recordId"] = record["id"]
                                info["value"] = record["value"]
                                cu_info.append(info)
                            if record["line"] == "电信":
                                info = {}
                                info["recordId"] = record["id"]
                                info["value"] = record["value"]
                                ct_info.append(info)
                        for line in lines:
                            if line == "CM":
                                changeDNS("CM", cm_info, temp_cf_cmips, domain, sub_domain, qcloud)
                            elif line == "CU":
                                changeDNS("CU", cu_info, temp_cf_cuips, domain, sub_domain, qcloud)
                            elif line == "CT":
                                changeDNS("CT", ct_info, temp_cf_ctips, domain, sub_domain, qcloud)
        except Exception as e:
            print("CHANGE DNS ERROR: ----Time: " + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "----MESSAGE: " + str(e))

if __name__ == '__main__':
    qcloud = QcloudApi()
    main(qcloud)
