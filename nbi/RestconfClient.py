import http.client as httpclient
import ssl
from base64 import b64encode


username="administrator"
password="e2e!Net4u#"
credential = b64decode(f"{username}:{password}".encode('utf-8')).decode("ascii")
auth={"Authorization" : "Basic %s" % credential }

rootheader={"Accept": "application/xrd+xml"}

conn = httpclient.HTTPSConnection('10.13.16.24',8181,context=ssl._create_stdlib_context(ssl.PROTOCOL_TLS))
conn.request("GET", "/.well-known/host-meta", headers={**rootheader, **auth)
res = conn.getresponse()
status = res.status
reason = res.reason
data = res.read()
print(data.decode('utf-8')) 
