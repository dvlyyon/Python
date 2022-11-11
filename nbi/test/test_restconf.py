import argparse
from nbi.restconf.client import (RestconfSession, RestconfCookieSession)

def convert_TLS_version(version_str):
    if version_str == 'TLSv1_2':
        return ssl.TLSVersion.TLSv1_2
    elif version_str == 'TLSv1_3':
        return ssl.TLSVersion.TLSv1_3
    else:
        return None

def test_get(args):
    session = RestconfSession(args.host, args.port, args.user_name, 
            args.passwd,scheme=args.scheme, ca=args.ca,
            certchain=(args.cert,args.key) if args.cert else None,
            minimum_version=convert_TLS_version(args.minimum_version) if args.minimum_version else None,
            maximum_version=convert_TLS_version(args.maximum_version) if args.maximum_version else None,
            curve=args.curve,
            keylog_filename=args.keylog_filename)
    print(session.connect())
    print(session.get(args.path,oformat=args.output_format))
    session.close()

def test_get_in_loop(args):
    if args.type == 'b':
        session = RestconfSession(args.host, args.port, args.user_name, 
                args.passwd,scheme=args.scheme, ca=args.ca,
                certchain=(args.cert,args.key) if args.cert else None,
                minimum_version=convert_TLS_version(args.minimum_version) if args.minimum_version else None,
                maximum_version=convert_TLS_version(args.maximum_version) if args.maximum_version else None,
                curve=args.curve,
                keylog_filename=args.keylog_filename)
    else:
        session = RestconfCookieSession(args.host, args.port, args.user_name, 
                args.passwd,scheme=args.scheme, ca=args.ca,
                certchain=(args.cert,args.key) if args.cert else None)

    print(session.connect())
    import time
    for i in range(args.loop):
        print(session.get(args.path))
        time.sleep(args.timeout)
    session.close()

def test_patch(args):
    session = RestconfSession(args.host, args.port, args.user_name, 
            args.passwd,scheme=args.scheme, ca=args.ca,
            certchain=(args.cert,args.key) if args.cert else None,
            minimum_version=convert_TLS_version(args.minimum_version) if args.minimum_version else None,
            maximum_version=convert_TLS_version(args.maximum_version) if args.maximum_version else None,
            curve=args.curve,
            keylog_filename=args.keylog_filename)
    print("...to continue")
    print(session.connect())
    url="ioa-network-element:ne/system/security/certificates/secure-applications/secure-application=HTTPFileClient"
    data="""
    <secure-application xmlns="http://infinera.com/yang/ioa/ne">
        <id>HTTPFileClient</id>
        <active-certificate-id></active-certificate-id>
    </secure-application>
    """
    print("...to patch")
    print(session.update(url,data,iformat='xml'))
    session.close()



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--host', required=True, help='The NE IP address')
    parser.add_argument('-p', '--port', default='8181', type=int, help='The Netconf Server port number')
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
    parser.add_argument('-l', '--loop', default='1000', type=int, help='times for retrieving')
    parser.add_argument('--timeout', default='3', type=int, help='interval between two neibor retrieving')
    parser.add_argument('--type', default='b', type=str, help='client type "b" or "c"')
    parser.add_argument('--scheme', default='https', type=str, help='client type "b" or "c"')
    parser.add_argument('-of', '--output_format', default='json', help='encoding in response')

    args = parser.parse_args()
    test_get(args)

