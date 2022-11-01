import http.client as httpclient
import ssl
from base64 import b64encode
import logging
import requests
import argparse

logger = logging.getLogger(__name__)
class RestconfSession():

    def __init__(self, host, port, username, password, scheme="https", ca=None, certchain=None, **kwargs):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.auth = {"Authorization" : "Basic %s" % b64encode(f"{username}:{password}".encode('utf-8')).decode('ascii') }
        self.root_header = {"Accept": "application/xrd+xml"}
        self.output_xml_header = {"Accept" : "application/yang-data+xml"}
        self.output_json_header = {"Accept" : "application/yang-data+json"}
        self.input_json_header = {"Content-Type" : "application/yang-data+json"}
        self.input_xml_header = {"Content-Type" : "application/yang-data+xml"}
        self.connection_header = {"Connection" : "Keep-Alive", "Keep-Alive": "timeout=5, max=100"}
        self.connection_close = {"Connection" : "close"}
        self.ca = ca
        self.cert = None
        self.key = None
        self.closed = True
        if certchain:
            self.cert = certchain[0]
            self.key = certchain[1]
        self.kwargs = kwargs
        self.conn = None

    def _fill_other_context(self,context: ssl.SSLContext):
        if self.kwargs.get("keylog_filename"):
            context.keylog_filename = self.kwargs["keylog_filename"]
        if self.kwargs.get("minimum_version"):
            context.minimum_version = self.kwargs["minimum_version"]
        if self.kwargs.get("maximum_version"):
            context.maximum_version = self.kwargs["maximum_version"]
        if self.kwargs.get("curve"):
            context.set_ecdh_curve(self.kwargs["curve"])
        if self.kwargs.get("ciphers"):
            context.set_ciphers(self.kwargs["ciphers"])

    def connect(self):
        try:
            if self.conn:
                self.conn.close()
            if self.ca:
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                context.load_verify_locations(self.ca)
            else:
                context = ssl.create_default_context()
            if self.cert:
                context.load_cert_chain(self.cert,self.key)

            self._fill_other_context(context)

            self.conn = httpclient.HTTPSConnection(self.host,self.port,context=context)
            self.conn.request("GET","/.well-known/host-meta", 
                    headers={**self.root_header, **self.auth})
            response = self.conn.getresponse()
            status = response.status
            reason = response.reason
            data = response.read()
            if status == 200:
                self.root_url = data.decode('utf-8').split("href='")[1].split("'")[0]
                self.closed = False
            return (status, reason, data.decode('utf-8'))
        except Exception as e:
            logger.exception(e)
            return (412, "Exception", str(e))

    def _parseresponse(self,response):
        status = response.status
        reason = response.reason
        data = response.read().decode('utf-8')
        headers = response.headers
        if headers.get("connection") and str(headers['connection']).strip() == 'close':
            self.closed = True
            
        return (status, reason, data)

    def get(self,url):
        try:
            if self.closed:
                self.connect() 
            self.conn.request("GET",f"{self.root_url}/data/{url}", headers={**self.output_json_header, **self.auth})
            response = self.conn.getresponse()
            return self._parseresponse(response)
        except Exception as e:
            logger.exception(e)
            return (412, "Exception", str(e))


    def patch(self,url,body):
        try:
            self.conn.request("PATCH",f"{self.root_url}/data/{url}",
                              headers={**self.output_json_header, **self.input_json_header, **self.auth},
                              body=body)
            response = self.conn.getresponse()
            return self._parseresponse(response)
        except Exception as e:
            logger.exception(e)
            return (412, "Exception", str(e))

    def create(self, url, body=None, method='POST', iformat='json', oformat='json'):
        headers = {}
        if iformat == 'xml':
            headers = {**self.input_xml_header, **headers}
        else:
            headers = {**self.input_json_header, **headers}

        if oformat == 'xml':
            headers = {**headers, **self.output_xml_header}
        else:
            headers = {**headers, **self.output_json_header}
        headers = {**headers, **self.auth}
        url = f"{self.root_url}/operations/{url}"
        
        if method == "PUT":
            return self.put(url,headers,body)
        else:
            return self.post(url,headers,body) 

    def post(self,url,headers,body):
        try:
            self.conn.request("POST",url,
                               headers=headers,
                               body=body)
            response = self.conn.getresponse()
            return self._parseresponse(response)
        except Exception as e:
            logger.exception(e)
            return (412, "Exception", str(e))

    def put(self,url,headers,body):
        try:
            self.conn.request("PUT",url,
                               headers=headers,
                               body=body)
            response = self.conn.getresponse()
            return self._parseresponse(response)
        except Exception as e:
            logger.exception(e)
            return (412, "Exception", str(e))

    def getStatus(self):
        try:
            response = self.conn.getresponse()
            return self._parseresponse(response)
        except Exception as e:
            logger.exception(e)
            return (412, "Exception", str(e))


    def close(self):
        if self.conn:
            self.conn.close()
        self.conn = None
        self.closed = True

class RestconfCookieSession:
    def __init__(self, host, port, username, password, scheme="https", ca=None, certchain=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.conn = requests.Session()
        self.baseurl = f"{scheme}://{host}:{port}"
        self.dataurl = f"{self.baseurl}/restconf/data"
        self.closed = True
        if ca:
            self.conn.verify = ca
        else:
            self.conn.verify = False
        if certchain:
            self.conn.cert = certchain

    def login(self):
        #self.conn.verify = False
        res=self.conn.post(f"{self.baseurl}/login", json={'username': self.username, 'password': self.password})
        return self._parseresponse(res)

    def connect(self):
        return self.login()

    def get(self, url):
        if self.closed:
            self.connect()
        res = self.conn.get(f"{self.dataurl}/{url}")
        return self._parseresponse(res)

    def patch(self,url,json):
        if self.closed:
            self.connect()
        res = self.conn.patch(url=f"{self.dataurl}/{url}",json=json)
        return self._parseresponse(res)

    def _parseresponse(self,response):
        status = response.status_code
        reason = response.reason
        data = response.text
        headers = response.headers
        #if status == 204 and self.conn.cookies:
        if self.conn.cookies:
            print("connected")
            for key in self.conn.cookies.keys():
                print(f'{key} --> {self.conn.cookies.get(key)}')
            self.closed = False
        if headers.get("connection") and str(headers['connection']).strip() == 'close':
            print("closed")
            self.closed = True
        return (status, reason, data)

    def logout(self):
        self.conn.post(f"{self.baseurl}/logout")

    def close(self):
        self.logout()

def convert_TLS_version(version_str):
    if version_str == 'TLSv1_2':
        return ssl.TLSVersion.TLSv1_2
    elif version_str == 'TLSv1_3':
        return ssl.TLSVersion.TLSv1_3
    else:
        return None

if __name__ == '__main__':
#    sess = RestconfSession("aaa.aaa.aaa.aaa",8181,"administrator","xxxxxxxx")
#    print(sess.connect())
#    s, r, d = sess.get("ioa-network-element:ne/equipment/card[name='1-5']")
#    print(d)

# username="adm"
# password="xxxxxxxx"
# credential = b64encode(f"{username}:{password}".encode('utf-8')).decode("ascii")
# auth={"Authorization" : "Basic %s" % credential }

# rootheader={"Accept": "application/xrd+xml"}
# rooturl = "/.well-known/host-meta"

# conn = httpclient.HTTPSConnection('10.13.16.24',8181,context=ssl._create_stdlib_context(ssl.PROTOCOL_TLS))
# conn.request("GET",rooturl, headers={**rootheader, **auth})
# res = conn.getresponse()
# status = res.status
# reason = res.reason
# data = res.read()
# print(data.decode('utf-8'))

# session = RestconfSession('aaa.aaa.aaa.aaa',8181,'xx','ssss')
# session.connect()
# url="ioa-network-element:ne/equipment/card=1-5"
# payload=b'{"ioa-network-element:card":[{"name":"1-5","alias-name":"test-alais"}]}'
# result, reason, output = session.patch(url,body=payload)
# print(result)
#session = RestconfCookieSession('172.29.202.84',8181,'administrator','e2e!Net4u#',scheme='https',ca='/home/david/Workspace/git/certificat/ecdsa_ca.crt',
#        certchain=('/home/david/Workspace/git/certificat/myne111.chain.crt','/home/david/Workspace/git/certificat/private/myne111.key'))
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--host', required=True, help='The NE IP address')
    parser.add_argument('-p', '--port', default='830', type=int, help='The Netconf Server port number')
    parser.add_argument('-u', '--user_name', required=True, help='The user name to login NE')
    parser.add_argument('-pw', '--passwd', required=True, help='The password for user to login NE')
    parser.add_argument('--path', required=True, help='The path is to retrieved')
    parser.add_argument('-ca', '--ca',  help='CA certificate')
    parser.add_argument('--cert',  help='client certificate')
    parser.add_argument('--key',  help='client key')
    parser.add_argument('-miv', '--minimum_version', default='None', help='minimum_version of TLS') 
    parser.add_argument('-mxv', '--maximum_version', default='None', help='maximum_version of TLS') 
    parser.add_argument('--curve', help='curve for ext key')
    parser.add_argument('-klf', '--keylog_filename', help='key log file')
    parser.add_argument('-l', '--loop', default='1000', type=int, help='times for retrieving')
    parser.add_argument('--timeout', default='3', type=int, help='interval between two neibor retrieving')
    parser.add_argument('--type', default='b', type=str, help='client type "b" or "c"')
    parser.add_argument('--scheme', default='https', type=str, help='client type "b" or "c"')

    args = parser.parse_args()
    if args.type == 'b':
        session = RestconfSession(args.host, args.port, args.user_name, 
                args.passwd,scheme=args.scheme, ca=args.ca,
                certchain=(args.cert,args.key) if args.cert else None,
                minimum_version=convert_TLS_version(args.minimum_version) if args.minimum_version else None,
                maximum_version=convert_TLS_version(args.maximum_version) if args.maximum_version else None,
                curve=args.curve,
                keylog_filename=args.keylog_filename)
    else:
        session = RestconfCookieSession(args.host, args.port, args.user_name, 
                args.passwd,scheme=args.scheme, ca=args.ca,
                certchain=(args.cert,args.key) if args.cert else None)

    print(session.connect())
    import time
    for i in range(args.loop):
        print(session.get(args.path))
        time.sleep(args.timeout)
    session.close()
