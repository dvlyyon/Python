from nbi.netconf.client import NetconfSession
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--host', required=True, help='The NE IP address')
    parser.add_argument('--port', default='830', type=int, help='The Netconf Server port number')
    parser.add_argument('-u', '--user_name', required=True, help='The user name to login NE')
    parser.add_argument('-p', '--passwd', required=True, help='The password for user to login NE')
    parser.add_argument('-f', '--rpc_file', required=True, help='The file defining RPC')
    parser.add_argument('-r', '--refresh', action="store_true", help='force to retrieve schema and translate again') 
    parser.add_argument('--pattern', default='',  help='is use to distigush private mode')
    args = parser.parse_args()
    return args
 
def get_connection(args):
    net_client = NetconfSession(ip=args.host,user=args.user_name,passwd=args.passwd,port=args.port)
    result, output = net_client.connect(timeout=120)
    return net_client

if __name__ == "__main__":
    args = parse_args()
    with open(args.rpc_file, 'r') as f:
        rpc_content = f.read()
    client = get_connection(args)
    result = client.call_rpc(rpc_content)
    print(result)
