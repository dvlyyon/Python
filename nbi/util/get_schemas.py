import os
import subprocess
import shutil
import argparse
import xml.dom.minidom as minidom

from nbi.netconf.client import NetconfSession
from nbi.ssh.client import SSHSession

def retrieve_schema(ip,port,user,password,yang_dir,pattern):
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
            prefix = ""
            items = pattern.split("||")
            if any([t in y.data for t in items]):
                prefix=f"{pattern.split('||')[0]}."
            with open(f"{yang_dir}/{prefix}{identifier}.yang", "w") as f:
                f.write(y.data)
    netconf_client.close()


def run(ip,port,user,password,force,pattern):
    cli_client = SSHSession(ip=ip,user=user,passwd=password)
    cli_client.connect()
    result, output = cli_client.sendCmd_without_connection_retry("swversion")
    version = None
    commands = []
    if result:
        lines = output.split("\n")
        for line in lines:
            columns = line.split()
            if " Active " in line:
                version = "R{}_{}".format(columns[5],columns[6].replace("-","_"))
                yang_dir = f"{version}/yang"
                commands.append(f"pyang -p {yang_dir} -f jstree -o ./{version}/private_{version}.html {yang_dir}/{pattern.split('||')[0]}*.yang")
                commands.append(f"pyang -p {yang_dir} -f jstree -o ./{version}/ietf_{version}.html {yang_dir}/iana-*.yang {yang_dir}/ietf-*.yang {yang_dir}/libnet*.yang {yang_dir}/n*.yang")
                commands.append(f"pyang -p {yang_dir} -f jstree -o ./{version}/openconfig_{version}.html {yang_dir}/openconfig-*.yang")
                break
            elif "-active" in line:
                version = "{}_{}".format(columns[2].split("-")[1],columns[2].split("-")[3])
                yang_dir = f"{version}/yang"
                command = f"pyang -p {yang_dir} -f jstree -o ./{version}/private_{version}.html {yang_dir}/{pattern.split('||')[0]}*.yang"
                commands.append(command)
                command = f"pyang -p {yang_dir} -f jstree -o ./{version}/ietf_{version}.html {yang_dir}/iana-*.yang {yang_dir}/ietf-*.yang {yang_dir}/libnet*.yang {yang_dir}/n*.yang"
                commands.append(command)
                break
    cli_client.close()

    if force and os.path.exists(version):
       shutil.rmtree(version)


    if not os.path.exists(yang_dir):
        os.mkdir(version)
        os.mkdir(yang_dir)
        retrieve_schema(ip=ip,user=user,port=port,password=password,yang_dir=yang_dir,pattern=pattern)
        for command in commands:
            result=subprocess.run(command,shell=True)
            print(result)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--host', required=True, help='The NE IP address')
    parser.add_argument('--port', default='830', type=int, help='The Netconf Server port number')
    parser.add_argument('-u', '--user_name', required=True, help='The user name to login NE')
    parser.add_argument('-p', '--passwd', required=True, help='The password for user to login NE')
    parser.add_argument('-r', '--refresh', action="store_true", help='force to retrieve schema and translate again') 
    parser.add_argument('--pattern', required=True, help='is use to distigush private mode')
    args = parser.parse_args()

    print(args.refresh)
    run(args.host, args.port, args.user_name, args.passwd, args.refresh, args.pattern)
