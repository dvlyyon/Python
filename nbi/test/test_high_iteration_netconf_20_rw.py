import time
import logging
from logging.handlers import RotatingFileHandler
from nbi.test_multiple_session import *

logger = logging.getLogger(__name__)

def main():
    write_oper = """
        <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <ne xmlns="http://infinera.com/yang/ioa/ne" xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
                <label>Changed by Netconf1</label>
            </ne>
        </config>"""
    method_para1 = (1000, 'aaa.aaa.aaa.aaa', 830, 'admin1', 'xxxxxxxx', [Command("/ne/equipment/card[name='1-5']")], 
                    [Command(command=write_oper)]
                    , True, True)

    test_parallel_sessions([
                            SessionTask('NETCONF', 20, netconf_session_thread, method_para1)
        ],3,12*3600)


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR, 
            format='%(asctime)s - %(threadName)s - %(levelname)s -  %(message)s',
            datefmt='%m-%d %H:%M')
    rfh = RotatingFileHandler('myapp.log', maxBytes=100*1024*1024, backupCount=20, mode='w')
    rfh.setLevel(logging.CRITICAL)
    fmt = logging.Formatter('%(asctime)s - %(threadName)s - %(levelname)s -  %(message)s',
            datefmt='%m-%d %H:%M')
    rfh.setFormatter(fmt)
    logging.root.addHandler(rfh)
    main()

