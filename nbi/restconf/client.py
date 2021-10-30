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
        self.json_content = {"Content-Type" : "application/yang-data+json"}
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

    def patch(self,url,body):
        self.conn.request("PATCH",f"{self.root_url}/data/{url}",
                          headers={**self.get_json_header, **self.json_content, **self.auth},
                          body=body)
        response = self.conn.getresponse()
        return self._parseresponse(response)

    def close(self):
        if self.conn:
            self.conn.close()
        self.conn = None

class RestconfCookieSession:
    import requests
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.conn = requests.Session()
        self.baseurl = f"https://{host}:{port}"
        self.dataurl = f"{self.baseurl}/restconf/data"
    def login(self):
        self.conn.verify = False
        res=self.conn.post(f"{self.baseurl}/login", json={'username': self.username, 'password': self.password}, verify=False)
        return self._parseresponse(res)

    def get(self, url):
        res = self.conn.get(f"{self.dataurl}/{url}")
        return self._parseresponse(res)

    def patch(self,url,json):
        res = self.conn.patch(url=f"{self.dataurl}/{url}",json=json)
        return self._parseresponse(res)

    def _parseresponse(self,response):
        status = response.status_code
        reason = response.reason
        data = response.text
        return (status, reason, data)

    def logout(self):
        self.conn.post(f"{self.baseurl}/logout")

if __name__ == '__main__':
#    sess = RestconfSession("aaa.aaa.aaa.84",8181,"administrator","xxxxxxx")
#    print(sess.connect())
#    s, r, d = sess.get("ioa-network-element:ne/equipment/card[name='1-5']")
#    print(d)

# username="administrator"
# password="xxxxxxx"
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

    session = RestconfSession('aaa.aaa.aaa.83',8181,'user','xxxxxx')
    session.connect()
    url="ioa-network-element:ne/equipment/card=1-5"
    payload=b'{"ioa-network-element:card":[{"name":"1-5","alias-name":"test-alais"}]}'
    result, reason, output = session.patch(url,body=payload)
    print(result)
