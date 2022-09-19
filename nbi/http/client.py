import http.client as httpclient
import ssl
from base64 import b64encode
import logging
import requests
import argparse

logger = logging.getLogger(__name__)
class HttpSession():

    def __init__(self, host, port, username, password, scheme="https", ca=None, certchain=None, **kwargs):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.auth = {"Authorization" : "Basic %s" % b64encode(f"{username}:{password}".encode('utf-8')).decode('ascii') }
        self.root_header = {"Accept": "application/text"}
        self.get_xml_header = {"Accept" : "application/xml"}
        self.get_json_header = {"Accept" : "application/json"}
        self.json_content = {"Content-Type" : "application/json"}
        self.connection_header = {"Connection" : "Keep-Alive", "Keep-Alive": "timeout=5, max=100"}
        self.connection_close = {"Connection" : "close"}
        self.ca = ca
        self.cert = None
        self.key = None
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
            self.conn.request("GET","/", 
                    headers={**self.root_header, **self.auth})
            response = self.conn.getresponse()
            status = response.status
            reason = response.reason
            data = response.read()
            if status == 200:
                self.root_url = ""
            return (status, reason, data.decode('utf-8'))
        except Exception as e:
            logger.exception(e)
            return (412, "Exception", str(e))

    def _parseresponse(self,response):
        status = response.status
        reason = response.reason
        data = response.read().decode('utf-8')
        return (status, reason, data)

    def get(self,url):
        try:
            self.conn.request("GET",f"{url}", headers={**self.get_json_header, **self.auth})
            response = self.conn.getresponse()
            return self._parseresponse(response)
        except Exception as e:
            logger.exception(e)
            return (412, "Exception", str(e))


    def patch(self,url,body):
        try:
            self.conn.request("PATCH",f"{self.root_url}/data/{url}",
                              headers={**self.get_json_header, **self.json_content, **self.auth},
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
    parser.add_argument('--path', required=True, help='The path is to retrieved')
    parser.add_argument('-ca', '--ca',  help='CA certificate')
    parser.add_argument('--cert',  help='client certificate')
    parser.add_argument('--key',  help='client key')
    parser.add_argument('-miv', '--minimum_version', default='None', help='minimum_version of TLS') 
    parser.add_argument('-mxv', '--maximum_version', default='None', help='maximum_version of TLS') 
    parser.add_argument('--curve', help='curve for ext key')
    parser.add_argument('-klf', '--keylog_filename', help='key log file')
    args = parser.parse_args()
    session = HttpSession(args.host, args.port, args.user_name, args.passwd,scheme='https',
            ca=args.ca,
            certchain=(args.cert,args.key) if args.cert else None,
            minimum_version=convert_TLS_version(args.minimum_version) if args.minimum_version else None,
            maximum_version=convert_TLS_version(args.maximum_version) if args.maximum_version else None,
            curve=args.curve,
            keylog_filename=args.keylog_filename)
    print(session.connect())
    import time
    for i in range(1000):
        print(session.get(args.path))
        time.sleep(3)
    session.close()
