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


default_conf = {
    "cf_api_key": "o1zrmHAF",
    "domains": {"hostxxnit.com":
                {"@": ["CM", "CU", "CT"],
                 "shop": ["CM", "CU", "CT"],
                 "stock": ["CM", "CU", "CT"]},
                "xxxx.me": {"@": ["CM", "CU", "CT"],
                            "vv": ["CM", "CU", "CT"]}
                },
    "affect_num": 2,
    "dns_server": 1,
    "region_hw": "",
    "region_ali": "",
    "ttl": 600,
    "record_type": "A",
    "secret_id": "",
    "secret_key": ""
}

# 添加配置文件
if not os.path.exists("config.json"):
    with open("config.json", "w") as f:
        json.dump(default_conf, f)
        log_error("已初始化配置文件，请修改 config.json")
        exit()
else:
    with open("config.json") as f:
        conf = json.load(f)
        log_info("成功加载 config.json")

# 可以从 https://shop.hostmonit.com 获取
KEY = conf["cf_api_key"]

# CM:移动 CU:联通 CT:电信  AB:境外 DEF:默认
# 修改需要更改的 DNSPod域名和子域名
DOMAINS = conf["domains"]

# 解析生效条数 免费的DNSPod相同线路最多支持2条解析
AFFECT_NUM = conf["affect_num"]

# DNS服务商 如果使用DNSPod改为1 如果使用阿里云解析改成2  如果使用华为云解析改成3
DNS_SERVER = conf["dns_server"]

# 如果使用华为云解析 需要从API凭证-项目列表中获取
REGION_HW = conf["region_hw"]

# 如果使用阿里云解析 REGION出现错误再修改 默认不需要修改 https://help.aliyun.com/document_detail/198326.html
REGION_ALI = conf["region_ali"]

# 解析生效时间，默认为600秒 如果不是DNS付费版用户 不要修改!!!
TTL = conf["ttl"]

# A为筛选出IPv4的IP  AAAA为筛选出IPv6的IP
RECORD_TYPE = conf["record_type"]

# API 密钥
# 腾讯云后台获取 https://console.cloud.tencent.com/cam/capi
# 阿里云后台获取 https://help.aliyun.com/document_detail/53045.html?spm=a2c4g.11186623.2.11.2c6a2fbdh13O53  注意需要添加DNS控制权限 AliyunDNSFullAccess
# 华为云后台获取 https://support.huaweicloud.com/devg-apisign/api-sign-provide-aksk.html
SECRETID = conf["secret_id"]
SECRETKEY = conf["secret_key"]


def get_optimization_ip():
    try:
        response = requests.post('https://api.hostmonit.com/get_optimization_ip', json={
                                 "key": KEY, "type": "v4" if RECORD_TYPE == "A" else "v6"}, headers={'Content-Type': 'application/json'})
        if response.status_code == 200:
            resp_json = response.json()
            if resp_json["code"] == 200:
                return resp_json
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
    if DNS_SERVER == 1:
        cloud = QcloudApiv3(SECRETID, SECRETKEY)
    elif DNS_SERVER == 2:
        cloud = AliApi(SECRETID, SECRETKEY, REGION_ALI)
    elif DNS_SERVER == 3:
        cloud = HuaWeiApi(SECRETID, SECRETKEY, REGION_HW)
    main(cloud)
