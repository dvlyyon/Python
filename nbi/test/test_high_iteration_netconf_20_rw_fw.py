import time
import logging
from logging.handlers import RotatingFileHandler
from nbi.test_high_iteration_framework import *

logger = logging.getLogger(__name__)

def main():
    write_oper = '''f"""
        <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <ne xmlns="http://infinera.com/yang/ioa/ne" xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
                <label>{threading.current_thread().getName()}</label>
            </ne>
        </config>"""'''
    method_para1 = (1000, ConnectContext('aaa.aaa.aaa.aaa', 830, 'admin1', 'xxxxxxxx'), 
            {"commands": 
                [Command(command=write_oper, kwargs={"mode": "w", "eval": True}),
                 Command(command="/ne/label", kwargs={"mode": "r"}),
                 Command(command="time.sleep(3)", kwargs={"mode": "r", "type": "ext"}),
                 Command(command="/ne/system/security/session", kwargs={"mode": "r"})
                 ] 
             },
             True, True, 5)

    test_parallel_sessions([
                            SessionTask('NETCONF', 20, method_para1)
                            ],
                            3,
                            12*3600)


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR, 
            format='%(asctime)s - %(threadName)s - %(levelname)s -  %(message)s',
            datefmt='%m-%d %H:%M')
    rfh = RotatingFileHandler("high_iteration_netconf_20_rw_fw.log", maxBytes=100*1024*1024, backupCount=20, mode='w')
    rfh.setLevel(logging.CRITICAL)
    fmt = logging.Formatter('%(asctime)s - %(threadName)s - %(levelname)s -  %(message)s',
            datefmt='%m-%d %H:%M')
    rfh.setFormatter(fmt)
    logging.root.addHandler(rfh)
    main()

