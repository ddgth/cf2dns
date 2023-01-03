#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Mail: tongdongdong@outlook.com
import random
import time
import os
import requests
from dns.qCloud import QcloudApiv3  # QcloudApiv3 DNSPod 的 API 更新了...
from dns.aliyun import AliApi
from dns.huawei import HuaWeiApi
import logging
import traceback
import json

log_cf2dns = logging.basicConfig(filename='cf2dns.log',
                                 format='%(asctime)s - %(levelname)s - %(message)s',
                                 level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S")


def log_error(msg: str):
    logging.error(msg)
    print(
        f'[Error] [{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}] {msg}')


def log_info(msg: str):
    logging.info(msg)
    print(
        f'[INFO] [{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}] {msg}')


# 可以从https://shop.hostmonit.com获取
try:
    KEY = os.environ["KEY"]
except KeyError:
    KEY = "o1zrmHAF"
# CM:移动 CU:联通 CT:电信 AB:境外 DEF:默认
# 修改需要更改的 DNSPod 域名和子域名
# {"hostmonit.com": {"@": ["CM","CU","CT"], "shop": ["CM", "CU", "CT"], "stock": ["CM","CU","CT"]},"4096.me": {"@": ["CM","CU","CT"], "vv": ["CM","CU","CT"]}}
DOMAINS = json.loads(os.environ["DOMAINS"])
# 腾讯云后台获取 https://console.cloud.tencent.com/cam/capi
SECRETID = os.environ["SECRETID"]  # 'AKIDV**********Hfo8CzfjgN'
SECRETKEY = os.environ["SECRETKEY"]  # 'ZrVs*************gqjOp1zVl'
# 默认为普通版本 不用修改
AFFECT_NUM = 2
# DNS服务商 如果使用DNSPod改为1 如果使用阿里云解析改成2  如果使用华为云解析改成3
DNS_SERVER = 1
# 如果试用华为云解析 需要从API凭证-项目列表中获取
REGION_HW = 'cn-east-3'
# 如果使用阿里云解析 REGION出现错误再修改 默认不需要修改 https://help.aliyun.com/document_detail/198326.html
REGION_ALI = 'cn-hongkong'
# 解析生效时间，默认为600秒 如果不是DNS付费版用户 不要修改!!!
TTL = 600
# A为筛选出IPv4的IP  AAAA为筛选出IPv6的IP
if len(sys.argv) >= 3:
    RECORD_TYPE = sys.argv[2]
else:
    RECORD_TYPE = "A"


def get_optimization_ip():
    try:

        response = requests.post('https://api.hostmonit.com/get_optimization_ip', json={
                                 "key": KEY, "type": "v4" if RECORD_TYPE == "A" else "v6"}, headers={'Content-Type': 'application/json'})
        if response.status_code == 200:
            return response.json()
        else:
            log_error(f'获取 Cloudflare IP 失败 {response.status_code}')
    except Exception as e:
        traceback.print_exc()
        log_error(f"获取 Cloudflare IP 失败 {str(e)}")


def changeDNS(line, c_info, domain, sub_domain, cloud):
    global AFFECT_NUM, RECORD_TYPE

    lines = {"CM": "移动", "CU": "联通", "CT": "电信", "AB": "境外", "DEF": "默认"}
    line = lines[line]

    try:
        create_num = AFFECT_NUM
        for i in range(create_num):
            if len(c_info) == 0:
                break
            cf_ip = c_info.pop(random.randint(0, len(c_info)-1))["ip"]
            cloud.create_record(
                domain, sub_domain, cf_ip, RECORD_TYPE, line, TTL)
            log_info(
                f'CREATE DNS SUCCESS - DOMAIN: {domain} SUBDOMAIN: {sub_domain} RECORDLINE: {line} VALUE: {cf_ip}')
    except Exception as e:
        traceback.print_exc()
        log_error(f'CHANGE DNS ERROR - MESSAGE: {str(e)}')


def main(cloud):
    global AFFECT_NUM, RECORD_TYPE
    if len(DOMAINS) > 0:
        try:
            cfips = get_optimization_ip()
            if cfips == None:
                log_error(f'GET CLOUDFLARE IP ERROR')
                return
            cf_cmips = cfips["info"]["CM"]
            cf_cuips = cfips["info"]["CU"]
            cf_ctips = cfips["info"]["CT"]
            for domain, sub_domains in DOMAINS.items():
                for sub_domain, lines in sub_domains.items():
                    # 删除对应 recordType 的解析
                    ret = cloud.get_record(domain, 20, sub_domain, RECORD_TYPE)
                    if ret["code"] == 0:
                        for record in ret["data"]["records"]:
                            if record["line"] == "移动" or record["line"] == "联通" or record["line"] == "电信":
                                retMsg = cloud.del_record(
                                    domain, record["id"])
                                if (retMsg["code"] == 0):
                                    log_info(
                                        f'DELETE DNS SUCCESS - DOMAIN: {domain} SUBDOMAIN: {sub_domain} RECORDLINE: {record["line"]}')
                                else:
                                    traceback.print_exc()
                                    log_error(
                                        f'DELETE DNS ERROR - DOMAIN: {domain} SUBDOMAIN: {sub_domain} RECORDLINE: {record["line"]} MESSAGE: {retMsg["message"]}')

                    # 重新创建对应 recordType 的 record
                    ret = cloud.get_record(
                        domain, 100, sub_domain, RECORD_TYPE)

                    if DNS_SERVER == 1 and "DP_Free" in ret["data"]["domain"]["grade"] and AFFECT_NUM > 2:
                        AFFECT_NUM = 2

                    for line in lines:
                        if line == "CM":
                            changeDNS("CM", cf_cmips,
                                      domain, sub_domain, cloud)
                        elif line == "CU":
                            changeDNS("CU", cf_cuips,
                                      domain, sub_domain, cloud)
                        elif line == "CT":
                            changeDNS("CT", cf_ctips,
                                      domain, sub_domain, cloud)
                        elif line == "AB":
                            changeDNS("AB", cf_ctips,
                                      domain, sub_domain, cloud)
                        elif line == "DEF":
                            changeDNS("DEF", cf_ctips,
                                      domain, sub_domain, cloud)
        except Exception as e:
            traceback.print_exc()
            log_error(f'CHANGE DNS ERROR - MESSAGE: {str(e)}')


if __name__ == '__main__':
    try:
        import requests
    except:
        os.system("pip install requests")

    if DNS_SERVER == 1:
        cloud = QcloudApiv3(SECRETID, SECRETKEY)
    elif DNS_SERVER == 2:
        cloud = AliApi(SECRETID, SECRETKEY, REGION_ALI)
    elif DNS_SERVER == 3:
        cloud = HuaWeiApi(SECRETID, SECRETKEY, REGION_HW)
    main(cloud)
