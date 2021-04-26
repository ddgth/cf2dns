import copy
import sys
import hashlib
import hmac
import binascii
from datetime import datetime

if sys.version_info.major < 3:
    from urllib import quote, unquote


    def hmacsha256(keyByte, message):
        return hmac.new(keyByte, message, digestmod=hashlib.sha256).digest()


    # Create a "String to Sign".
    def StringToSign(canonicalRequest, t):
        bytes = HexEncodeSHA256Hash(canonicalRequest)
        return "%s\n%s\n%s" % (Algorithm, datetime.strftime(t, BasicDateFormat), bytes)

else:
    from urllib.parse import quote, unquote


    def hmacsha256(keyByte, message):
        return hmac.new(keyByte.encode('utf-8'), message.encode('utf-8'), digestmod=hashlib.sha256).digest()


    # Create a "String to Sign".
    def StringToSign(canonicalRequest, t):
        bytes = HexEncodeSHA256Hash(canonicalRequest.encode('utf-8'))
        return "%s\n%s\n%s" % (Algorithm, datetime.strftime(t, BasicDateFormat), bytes)


def urlencode(s):
    return quote(s, safe='~')


def findHeader(r, header):
    for k in r.headers:
        if k.lower() == header.lower():
            return r.headers[k]
    return None


# HexEncodeSHA256Hash returns hexcode of sha256
def HexEncodeSHA256Hash(data):
    sha256 = hashlib.sha256()
    sha256.update(data)
    return sha256.hexdigest()


# HWS API Gateway Signature
class HttpRequest:
    def __init__(self, method="", url="", headers=None, body=""):
        self.method = method
        spl = url.split("://", 1)
        scheme = 'http'
        if len(spl) > 1:
            scheme = spl[0]
            url = spl[1]
        query = {}
        spl = url.split('?', 1)
        url = spl[0]
        if len(spl) > 1:
            for kv in spl[1].split("&"):
                spl = kv.split("=", 1)
                key = spl[0]
                value = ""
                if len(spl) > 1:
                    value = spl[1]
                if key != '':
                    key = unquote(key)
                    value = unquote(value)
                    if key in query:
                        query[key].append(value)
                    else:
                        query[key] = [value]
        spl = url.split('/', 1)
        host = spl[0]
        if len(spl) > 1:
            url = '/' + spl[1]
        else:
            url = '/'

        self.scheme = scheme
        self.host = host
        self.uri = url
        self.query = query
        if headers is None:
            self.headers = {}
        else:
            self.headers = copy.deepcopy(headers)
        if sys.version_info.major < 3:
            self.body = body
        else:
            self.body = body.encode("utf-8")


BasicDateFormat = "%Y%m%dT%H%M%SZ"
Algorithm = "SDK-HMAC-SHA256"
HeaderXDate = "X-Sdk-Date"
HeaderHost = "host"
HeaderAuthorization = "Authorization"
HeaderContentSha256 = "x-sdk-content-sha256"


# Build a CanonicalRequest from a regular request string
#
# CanonicalRequest =
#  HTTPRequestMethod + '\n' +
#  CanonicalURI + '\n' +
#  CanonicalQueryString + '\n' +
#  CanonicalHeaders + '\n' +
#  SignedHeaders + '\n' +
#  HexEncode(Hash(RequestPayload))
def CanonicalRequest(r, signedHeaders):
    canonicalHeaders = CanonicalHeaders(r, signedHeaders)
    hexencode = findHeader(r, HeaderContentSha256)
    if hexencode is None:
        hexencode = HexEncodeSHA256Hash(r.body)
    return "%s\n%s\n%s\n%s\n%s\n%s" % (r.method.upper(), CanonicalURI(r), CanonicalQueryString(r),
                                       canonicalHeaders, ";".join(signedHeaders), hexencode)


def CanonicalURI(r):
    pattens = unquote(r.uri).split('/')
    uri = []
    for v in pattens:
        uri.append(urlencode(v))
    urlpath = "/".join(uri)
    if urlpath[-1] != '/':
        urlpath = urlpath + "/"  # always end with /
    # r.uri = urlpath
    return urlpath


def CanonicalQueryString(r):
    keys = []
    for key in r.query:
        keys.append(key)
    keys.sort()
    a = []
    for key in keys:
        k = urlencode(key)
        value = r.query[key]
        if type(value) is list:
            value.sort()
            for v in value:
                kv = k + "=" + urlencode(str(v))
                a.append(kv)
        else:
            kv = k + "=" + urlencode(str(value))
            a.append(kv)
    return '&'.join(a)


def CanonicalHeaders(r, signedHeaders):
    a = []
    __headers = {}
    for key in r.headers:
        keyEncoded = key.lower()
        value = r.headers[key]
        valueEncoded = value.strip()
        __headers[keyEncoded] = valueEncoded
        if sys.version_info.major == 3:
            r.headers[key] = valueEncoded.encode("utf-8").decode('iso-8859-1')
    for key in signedHeaders:
        a.append(key + ":" + __headers[key])
    return '\n'.join(a) + "\n"


def SignedHeaders(r):
    a = []
    for key in r.headers:
        a.append(key.lower())
    a.sort()
    return a


# Create the HWS Signature.
def SignStringToSign(stringToSign, signingKey):
    hm = hmacsha256(signingKey, stringToSign)
    return binascii.hexlify(hm).decode()


# Get the finalized value for the "Authorization" header.  The signature
# parameter is the output from SignStringToSign
def AuthHeaderValue(signature, AppKey, signedHeaders):
    return "%s Access=%s, SignedHeaders=%s, Signature=%s" % (
        Algorithm, AppKey, ";".join(signedHeaders), signature)


class Signer:
    def __init__(self):
        self.Key = ""
        self.Secret = ""

    def Verify(self, r, authorization):
        if sys.version_info.major == 3 and isinstance(r.body, str):
            r.body = r.body.encode('utf-8')
        headerTime = findHeader(r, HeaderXDate)
        if headerTime is None:
            return False
        else:
            t = datetime.strptime(headerTime, BasicDateFormat)

        signedHeaders = SignedHeaders(r)
        canonicalRequest = CanonicalRequest(r, signedHeaders)
        stringToSign = StringToSign(canonicalRequest, t)
        return authorization == SignStringToSign(stringToSign, self.Secret)

    # SignRequest set Authorization header
    def Sign(self, r):
        if sys.version_info.major == 3 and isinstance(r.body, str):
            r.body = r.body.encode('utf-8')
        headerTime = findHeader(r, HeaderXDate)
        if headerTime is None:
            t = datetime.utcnow()
            r.headers[HeaderXDate] = datetime.strftime(t, BasicDateFormat)
        else:
            t = datetime.strptime(headerTime, BasicDateFormat)

        haveHost = False
        for key in r.headers:
            if key.lower() == 'host':
                haveHost = True
                break
        if not haveHost:
            r.headers["host"] = r.host
        signedHeaders = SignedHeaders(r)
        canonicalRequest = CanonicalRequest(r, signedHeaders)
        stringToSign = StringToSign(canonicalRequest, t)
        signature = SignStringToSign(stringToSign, self.Secret)
        authValue = AuthHeaderValue(signature, self.Key, signedHeaders)
        r.headers[HeaderAuthorization] = authValue
        r.headers["content-length"] = str(len(r.body))
        queryString = CanonicalQueryString(r)
        if queryString != "":
            r.uri = r.uri + "?" + queryString
