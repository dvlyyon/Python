import os
import subprocess
import shutil
import argparse
import xml.dom.minidom as minidom

from nbi.netconf.client import NetconfSession

def run(ip,port,user,password):

    netconf_client = NetconfSession(ip=ip,user=user,passwd=password,port=port)
    netconf_client.connect()
    result, output = netconf_client.get_schema_list()
    doc = minidom.parseString(output)
    node = doc.documentElement
    schemas = doc.getElementsByTagName("schema")
    yang_dir = "./tmp_yang_dir"
    if os.path.exists(yang_dir):
        shutil.rmtree(yang_dir)
    os.mkdir(yang_dir)
    for schema in schemas:
        identifier = schema.getElementsByTagName("identifier")[0].childNodes[0].data
        version = schema.getElementsByTagName("version")[0].childNodes[0].data
        fmt = schema.getElementsByTagName("format")[0].childNodes[0].data
        if fmt == "yang":
            r, y = netconf_client.get_schema(identifier,version,fmt)
            with open(f"{yang_dir}/{identifier}.yang", "w") as f:
                f.write(y.data)
    result=subprocess.run(f"pyang -p {yang_dir} -f jstree -o ./gr.html {yang_dir}/ne.yang",shell=True)
    print(result)
    netconf_client.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--host', required=True, help='The NE IP address')
    parser.add_argument('-p', '--port', default='830', help='The Netconf Server port number')
    parser.add_argument('-u', '--user_name', required=True, help='The user name to login NE')
    parser.add_argument('--passwd', required=True, help='The password for user to login NE')
    args = parser.parse_args()

    run(args.host, args.port, args.user_name, args.passwd)
