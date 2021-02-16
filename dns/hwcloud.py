import json
import requests
import signer


class Hwcloud:
    def __init__(self, AK, SK):
        self.sign = signer.Signer()
        self.sign.Key = AK
        self.sign.Secret = SK

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

    def del_record(self, domain: str, record: str):
        zone_id = self.get_zone_id(domain)
        if zone_id != "The domain doesn't exist":
            url = 'https://dns.myhuaweicloud.com/v2/zones/' + zone_id + '/recordsets/' + record
        else:
            return "The domain doesn't exist"
        r = signer.HttpRequest('DELETE', url)
        self.sign.Sign(r)
        res = json.loads(requests.delete(url, headers=r.headers).text)
        print(res['status'])
        if res['status'] == 'PENDING_DELETE':
            return 'success'

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
        for i in range(0, len(res['recordsets'])):
            if res['recordsets'][i]['name'].split('.')[0] == sub_domain and res['recordsets'][i]['type'] == record_type:
                records = res['recordsets'][i]['records']
                recordset_id = res['recordsets'][i]['id']
        if records and recordset_id != '':
            return records, recordset_id
        else:
            return "The sub domain doesn't exist"

    def create_record(self, domain: str, sub_domain: str, value: str, record_type: str, line: str, ttl: int):
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
            "records": [
                value
            ],
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
    # print(api.get_zone_id('ravizhan.top'))
    # print(api.get_record('ravizhan.top',20,'abc','A'))
    # print(api.del_record('ravizhan.top','8aace3ba763e2fd50177a570199f5ffe'))
    # print(api.create_record('ravizhan.top','abc','1.1.1.1','A','联通',1))
    # print(api.change_record('ravizhan.top','8aace3b9763e2fc70177a98e37357976','1.2.3.4',10))
