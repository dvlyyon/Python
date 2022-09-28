import ssl
from base64 import b64encode
import logging
import requests
import argparse

logger = logging.getLogger(__name__)

class HttpFileSession:
    def __init__(self, host, port, username, password, scheme="https", ca=None, certchain=None):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.conn = requests.Session()
        self.baseurl = f"{scheme}://{host}:{port}"
        if ca:
            self.conn.verify = ca
        else:
            self.conn.verify = False
        if certchain:
            self.conn.cert = certchain
        self.auth = requests.auth.HTTPBasicAuth(self.username, self.password)
        self.conn.auth = self.auth

    def login(self):
        #self.conn.verify = False
        res=self.conn.post(f"{self.baseurl}/login", auth=self.auth)
        return self._parseresponse(res)

    def connect(self):
        return self.login()

    def get(self, url):
        res = self.conn.get(f"{self.baseurl}/{url}")
        return self._parseresponse(res)

    def post_file(self, url, file_path):
        filedata = open(file_path, "rb")
        res = self.conn.post(url=f'{self.baseurl}/{url}', auth = self.auth, files={"file": filedata})
        return self._parseresponse(res)

    def put_file(self, url, file_path):
        filedata = open(file_path, "rb")
        res = self.conn.put(url=f'{self.baseurl}/{url}', files={"file": filedata})
        return self._parseresponse(res)

    def patch(self,url,json):
        res = self.conn.patch(url=f"{self.baseurl}/{url}",json=json)
        return self._parseresponse(res)

    def _parseresponse(self,response):
        status = response.status_code
        reason = response.reason
        data = response.text
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
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--host', required=True, help='The NE IP address')
    parser.add_argument('-p', '--port', default='830', type=int, help='The Netconf Server port number')
    parser.add_argument('-u', '--user_name', required=True, help='The user name to login NE')
    parser.add_argument('-pw', '--passwd', required=True, help='The password for user to login NE')
    parser.add_argument('-ca', '--ca',  help='CA certificate')
    parser.add_argument('--cert',  help='client certificate')
    parser.add_argument('--key',  help='client key')
    parser.add_argument('--timeout', default=3, help='time to next round')
    parser.add_argument('--loop', default=1000, help='time to next round')
    # parser.add_argument('-miv', '--minimum_version', default='None', help='minimum_version of TLS') 
    # parser.add_argument('-mxv', '--maximum_version', default='None', help='maximum_version of TLS') 
    # parser.add_argument('--curve', help='curve for ext key')
    # parser.add_argument('-klf', '--keylog_filename', help='key log file')
    args = parser.parse_args()
    # session = RestconfSession(args.host, args.port, args.user_name, args.passwd,scheme='https',
            # ca=args.ca,
            # certchain=(args.cert,args.key) if args.cert else None,
            # minimum_version=convert_TLS_version(args.minimum_version) if args.minimum_version else None,
            # maximum_version=convert_TLS_version(args.maximum_version) if args.maximum_version else None,
            # curve=args.curve,
            # keylog_filename=args.keylog_filename)
    # print(session.connect())
    session =  HttpFileSession(args.host,args.port,args.user_name,args.passwd,
        ca=args.ca, certchain=(args.cert,args.key) if args.cert else None)
    import time
    for i in range(int(args.loop)):
        print(session.put_file(url=f'transfer/myfile{i}.p7b',file_path='/home/david/Workspace/git/certificat/ca.p7b'))
        time.sleep(args.timeout)
        

