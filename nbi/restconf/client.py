import http.client as httpclient
import ssl
from base64 import b64encode

class RestconfSession():

    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.auth = {"Authorization" : "Basic %s" % b64encode(f"{username}:{password}".encode('utf-8')).decode('ascii') }
        self.root_header = {"Accept": "application/xrd+xml"}
        self.get_xml_header = {"Accept" : "application/yang-data+xml"}
        self.get_json_header = {"Accept" : "application/yang-data+json"}
        self.conn = None

    def connect(self):
        if self.conn:
            self.conn.close()
        self.conn = httpclient.HTTPSConnection(self.host,self.port,context=ssl._create_stdlib_context(ssl.PROTOCOL_TLS))
        self.conn.request("GET","/.well-known/host-meta", headers={**self.root_header, **self.auth})
        response = self.conn.getresponse()
        status = response.status
        reason = response.reason
        data = response.read()
        if status == 200:
            self.root_url = data.decode('utf-8').split("href='")[1].split("'")[0]
        return (status, reason, data.decode('utf-8'))

    def _parseresponse(self,response):
        status = response.status
        reason = response.reason
        data = response.read().decode('utf-8')
        return (status, reason, data)

    def get(self,url):
        self.conn.request("GET",f"{self.root_url}/data/{url}", headers={**self.get_json_header, **self.auth})
        response = self.conn.getresponse()
        return self._parseresponse(response)

    def close(self):
        if self.conn:
            self.conn.close()
        self.conn = None

if __name__ == '__main__':
    sess = RestconfSession("172.29.202.84",8181,"administrator","e2e!Net4u#")
    print(sess.connect())
    s, r, d = sess.get("ioa-network-element:ne/equipment/card[name='1-5']")
    print(d)
# username="administrator"
# password="e2e!Net4u#"
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
