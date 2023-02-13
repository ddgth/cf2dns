#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Mail: tongdongdong@outlook.com
import random
import time
import requests
from dns.qCloud import QcloudApiv3 # QcloudApiv3 DNSPod 的 API 更新了 By github@z0z0r4
from dns.aliyun import AliApi
from dns.huawei import HuaWeiApi
from log import Logger
import traceback

#可以从https://shop.hostmonit.com获取
KEY = "o1zrmHAF"

#CM:移动 CU:联通 CT:电信  AB:境外 DEF:默认
#修改需要更改的dnspod域名和子域名
DOMAINS = {
    "hostxxnit.com": {"@": ["CM","CU","CT"], "shop": ["CM", "CU", "CT"], "stock": ["CM","CU","CT"]},
    "484848.xyz": {"@": ["CM","CU","CT"], "shop": ["CM","CU","CT"]}
}

#解析生效条数 免费的DNSPod相同线路最多支持2条解析
AFFECT_NUM = 2

#DNS服务商 如果使用DNSPod改为1 如果使用阿里云解析改成2  如果使用华为云解析改成3
DNS_SERVER = 1

#如果使用华为云解析 需要从API凭证-项目列表中获取
REGION_HW = 'cn-east-3'

#如果使用阿里云解析 REGION出现错误再修改 默认不需要修改 https://help.aliyun.com/document_detail/198326.html
REGION_ALI = 'cn-hongkong'

#解析生效时间，默认为600秒 如果不是DNS付费版用户 不要修改!!!
TTL = 600

#v4为筛选出IPv4的IP  v6为筛选出IPv6的IP
TYPE = 'v4'

#API 密钥
#腾讯云后台获取 https://console.cloud.tencent.com/cam/capi
#阿里云后台获取 https://help.aliyun.com/document_detail/53045.html?spm=a2c4g.11186623.2.11.2c6a2fbdh13O53  注意需要添加DNS控制权限 AliyunDNSFullAccess
#华为云后台获取 https://support.huaweicloud.com/devg-apisign/api-sign-provide-aksk.html
SECRETID = 'WTTCWxxxxxxxxxxxxxxxxxxxxx84O0V'
SECRETKEY = 'GXkG6D4X1Nxxxxxxxxxxxxxxxxxxxxx4lRg6lT'

log_cf2dns = Logger('cf2dns.log', level='debug') 

def get_optimization_ip():
    try:
        headers = headers = {'Content-Type': 'application/json'}
        data = {"key": KEY, "type": TYPE}
        response = requests.post('https://api.hostmonit.com/get_optimization_ip', json=data, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            log_cf2dns.logger.error("CHANGE OPTIMIZATION IP ERROR: ----Time: " + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "----MESSAGE: REQUEST STATUS CODE IS NOT 200")
            return None
    except Exception as e:
        log_cf2dns.logger.error("CHANGE OPTIMIZATION IP ERROR: ----Time: " + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "----MESSAGE: " + str(e))
        return None

def changeDNS(line, s_info, c_info, domain, sub_domain, cloud):
    global AFFECT_NUM, TYPE
    if TYPE == 'v6':
        recordType = "AAAA"
    else:
        recordType = "A"

    lines = {"CM": "移动", "CU": "联通", "CT": "电信", "AB": "境外", "DEF": "默认"}
    line = lines[line]

    try:
        create_num = AFFECT_NUM - len(s_info)
        if create_num == 0:
            for info in s_info:
                if len(c_info) == 0:
                    break
                cf_ip = c_info.pop(random.randint(0,len(c_info)-1))["ip"]
                if cf_ip in str(s_info):
                    continue
                ret = cloud.change_record(domain, info["recordId"], sub_domain, cf_ip, recordType, line, TTL)
                if(DNS_SERVER != 1 or ret["code"] == 0):
                    log_cf2dns.logger.info("CHANGE DNS SUCCESS: ----Time: " + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "----DOMAIN: " + domain + "----SUBDOMAIN: " + sub_domain + "----RECORDLINE: "+line+"----RECORDID: " + str(info["recordId"]) + "----VALUE: " + cf_ip )
                else:
                    log_cf2dns.logger.error("CHANGE DNS ERROR: ----Time: " + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "----DOMAIN: " + domain + "----SUBDOMAIN: " + sub_domain + "----RECORDLINE: "+line+"----RECORDID: " + str(info["recordId"]) + "----VALUE: " + cf_ip + "----MESSAGE: " + ret["message"] )
        elif create_num > 0:
            for i in range(create_num):
                if len(c_info) == 0:
                    break
                cf_ip = c_info.pop(random.randint(0,len(c_info)-1))["ip"]
                if cf_ip in str(s_info):
                    continue
                ret = cloud.create_record(domain, sub_domain, cf_ip, recordType, line, TTL)
                if(DNS_SERVER != 1 or ret["code"] == 0):
                    log_cf2dns.logger.info("CREATE DNS SUCCESS: ----Time: " + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "----DOMAIN: " + domain + "----SUBDOMAIN: " + sub_domain + "----RECORDLINE: "+line+"----VALUE: " + cf_ip )
                else:
                    log_cf2dns.logger.error("CREATE DNS ERROR: ----Time: " + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "----DOMAIN: " + domain + "----SUBDOMAIN: " + sub_domain + "----RECORDLINE: "+line+"----RECORDID: " + str(info["recordId"]) + "----VALUE: " + cf_ip + "----MESSAGE: " + ret["message"] )
        else:
            for info in s_info:
                if create_num == 0 or len(c_info) == 0:
                    break
                cf_ip = c_info.pop(random.randint(0,len(c_info)-1))["ip"]
                if cf_ip in str(s_info):
                    create_num += 1
                    continue
                ret = cloud.change_record(domain, info["recordId"], sub_domain, cf_ip, recordType, line, TTL)
                if(DNS_SERVER != 1 or ret["code"] == 0):
                    log_cf2dns.logger.info("CHANGE DNS SUCCESS: ----Time: " + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "----DOMAIN: " + domain + "----SUBDOMAIN: " + sub_domain + "----RECORDLINE: "+line+"----RECORDID: " + str(info["recordId"]) + "----VALUE: " + cf_ip )
                else:
                    log_cf2dns.logger.error("CHANGE DNS ERROR: ----Time: " + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "----DOMAIN: " + domain + "----SUBDOMAIN: " + sub_domain + "----RECORDLINE: "+line+"----RECORDID: " + str(info["recordId"]) + "----VALUE: " + cf_ip + "----MESSAGE: " + ret["message"] )
                create_num += 1
    except Exception as e:
            log_cf2dns.logger.error("CHANGE DNS ERROR: ----Time: " + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "----MESSAGE: " + str(e))

def main(cloud):
    global AFFECT_NUM, TYPE
    if TYPE == 'v6':
        recordType = "AAAA"
    else:
        recordType = "A"
    if len(DOMAINS) > 0:
        try:
            cfips = get_optimization_ip()
            if cfips == None or cfips["code"] != 200:
                log_cf2dns.logger.error("GET CLOUDFLARE IP ERROR: ----Time: " + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "----MESSAGE: " + str(cfips["info"]))
                return
            cf_cmips = cfips["info"]["CM"]
            cf_cuips = cfips["info"]["CU"]
            cf_ctips = cfips["info"]["CT"]
            for domain, sub_domains in DOMAINS.items():
                for sub_domain, lines in sub_domains.items():
                    temp_cf_cmips = cf_cmips.copy()
                    temp_cf_cuips = cf_cuips.copy()
                    temp_cf_ctips = cf_ctips.copy()
                    temp_cf_abips = cf_ctips.copy()
                    temp_cf_defips = cf_ctips.copy()
                    if DNS_SERVER == 1:
                        ret = cloud.get_record(domain, 20, sub_domain, "CNAME")
                        if ret["code"] == 0:
                            for record in ret["data"]["records"]:
                                if record["line"] == "移动" or record["line"] == "联通" or record["line"] == "电信":
                                    retMsg = cloud.del_record(domain, record["id"])
                                    if(retMsg["code"] == 0):
                                        log_cf2dns.logger.info("DELETE DNS SUCCESS: ----Time: "  + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "----DOMAIN: " + domain + "----SUBDOMAIN: " + sub_domain + "----RECORDLINE: "+record["line"] )
                                    else:
                                        log_cf2dns.logger.error("DELETE DNS ERROR: ----Time: "  + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "----DOMAIN: " + domain + "----SUBDOMAIN: " + sub_domain + "----RECORDLINE: "+record["line"] + "----MESSAGE: " + retMsg["message"] )
                    ret = cloud.get_record(domain, 100, sub_domain, recordType)
                    if DNS_SERVER != 1 or ret["code"] == 0 :
                        if DNS_SERVER == 1 and "Free" in ret["data"]["domain"]["grade"] and AFFECT_NUM > 2:
                            AFFECT_NUM = 2
                        cm_info = []
                        cu_info = []
                        ct_info = []
                        ab_info = []
                        def_info = []
                        for record in ret["data"]["records"]:
                            info = {}
                            info["recordId"] = record["id"]
                            info["value"] = record["value"]
                            if record["line"] == "移动":
                                cm_info.append(info)
                            elif record["line"] == "联通":
                                cu_info.append(info)
                            elif record["line"] == "电信":
                                ct_info.append(info)
                            elif record["line"] == "境外":
                                ab_info.append(info)
                            elif record["line"] == "默认":
                                def_info.append(info)
                        for line in lines:
                            if line == "CM":
                                changeDNS("CM", cm_info, temp_cf_cmips, domain, sub_domain, cloud)
                            elif line == "CU":
                                changeDNS("CU", cu_info, temp_cf_cuips, domain, sub_domain, cloud)
                            elif line == "CT":
                                changeDNS("CT", ct_info, temp_cf_ctips, domain, sub_domain, cloud)
                            elif line == "AB":
                                changeDNS("AB", ab_info, temp_cf_abips, domain, sub_domain, cloud)
                            elif line == "DEF":
                                changeDNS("DEF", def_info, temp_cf_defips, domain, sub_domain, cloud)
        except Exception as e:
            traceback.print_exc()  
            log_cf2dns.logger.error("CHANGE DNS ERROR: ----Time: " + str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) + "----MESSAGE: " + str(e))

if __name__ == '__main__':
    if DNS_SERVER == 1:
        cloud = QcloudApiv3(SECRETID, SECRETKEY)
    elif DNS_SERVER == 2:
        cloud = AliApi(SECRETID, SECRETKEY, REGION_ALI)
    elif DNS_SERVER == 3:
        cloud = HuaWeiApi(SECRETID, SECRETKEY, REGION_HW)
    main(cloud)