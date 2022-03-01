import os
import subprocess
import shutil
import argparse
import xml.dom.minidom as minidom

from nbi.netconf.client import NetconfSession
from nbi.ssh.client import SSHSession

def retrieve_schema(ip,port,user,password,yang_dir):
    netconf_client = NetconfSession(ip=ip,user=user,passwd=password,port=port)
    netconf_client.connect()
    result, output = netconf_client.get_schema_list()
    doc = minidom.parseString(output)
    node = doc.documentElement
    schemas = doc.getElementsByTagName("schema")
    for schema in schemas:
        identifier = schema.getElementsByTagName("identifier")[0].childNodes[0].data
        version = schema.getElementsByTagName("version")[0].childNodes[0].data
        fmt = schema.getElementsByTagName("format")[0].childNodes[0].data
        if fmt == "yang":
            r, y = netconf_client.get_schema(identifier,version,fmt)
            with open(f"{yang_dir}/{identifier}.yang", "w") as f:
                f.write(y.data)
    netconf_client.close()


def run(ip,port,user,password):
    cli_client = SSHSession(ip=ip,user=user,passwd=password)
    cli_client.connect()
    result, output = cli_client.sendCmd_without_connection_retry("swversion")
    version = None
    command = None
    if result:
        lines = output.split("\n")
        for line in lines:
            columns = line.split()
            if " Active " in line:
                version = "R{}_{}".format(columns[5],columns[6].replace("-","_"))
                yang_dir = f"{version}/yang"
                command = f"pyang -p {yang_dir} -f jstree -o ./{version}/{version}.html {yang_dir}/ne.yang {yang_dir}/fault-management.yang"
                break
            elif "-active" in line:
                version = "{}_{}".format(columns[2].split("-")[1],columns[2].split("-")[3])
                yang_dir = f"{version}/yang"
                command = f"pyang -p {yang_dir} -f jstree -o ./{version}/{version}.html {yang_dir}/ioa-network-element.yang {yang_dir}/ioa-alarm.yang {yang_dir}/ioa-pm.yang"
                break
    cli_client.close()

    if not os.path.exists(yang_dir):
       # shutil.rmtree(yang_dir)
        os.mkdir(version)
        os.mkdir(yang_dir)
        retrieve_schema(ip=ip,user=user,port=port,password=password,yang_dir=yang_dir)
        result=subprocess.run(command,shell=True)
        print(result)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--host', required=True, help='The NE IP address')
    parser.add_argument('-p', '--port', default='830', help='The Netconf Server port number')
    parser.add_argument('-u', '--user_name', required=True, help='The user name to login NE')
    parser.add_argument('--passwd', required=True, help='The password for user to login NE')
    args = parser.parse_args()

    run(args.host, args.port, args.user_name, args.passwd)
