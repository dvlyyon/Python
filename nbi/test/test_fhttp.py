import argparse
import time
import ssl
from nbi.http.fclient import HttpFileSession

def test_put_in_loop(args):
    session =  HttpFileSession(args.host,args.port,args.user_name,args.passwd,
        ca=args.ca, certchain=(args.cert,args.key) if args.cert else None)
    for i in range(int(args.loop)):
        print(session.put_file(url=f'transfer/myfile{i}.p7b',file_path='/home/david/Workspace/git/certificat/ca.p7b'))
        time.sleep(args.timeout)




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
    args = parser.parse_args()
    test_put_in_loop(args)
