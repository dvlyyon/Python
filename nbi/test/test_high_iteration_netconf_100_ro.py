import time
import logging
from logging.handlers import RotatingFileHandler
from nbi.test_multiple_session import *

logger = logging.getLogger(__name__)

def main():
    method_para1 = (1000, 'aaa.aaa.aaa.aaa', 830, 'admin1', 'xxxxxxxx', [Command("/ne/equipment/card[name='1-5']")], 
                    None, True)
    method_para2 = (1000, 'aaa.aaa.aaa.aaa', 830, 'admin2', 'xxxxxxxx', [Command("/ne/equipment/card[name='1-5']")], 
                    None, True,True)
    method_para3 = (1000, 'aaa.aaa.aaa.aaa', 830, 'admin3', 'xxxxxxxx', [Command("/ne/equipment/card[name='1-5']")], 
                    None, True,True)
    method_para4 = (1000, 'aaa.aaa.aaa.aaa', 830, 'admin4', 'xxxxxxxx', [Command("/ne/equipment/card[name='1-5']")], 
                    None, True,True)
    method_para5 = (1000, 'aaa.aaa.aaa.aaa', 830, 'admin5', 'xxxxxxxx', [Command("/ne/equipment/card[name='1-5']")], 
                    None, True)

    test_parallel_sessions([
                            SessionTask('NETCONF', 20, netconf_session_thread, method_para1),
                            SessionTask('NETCONF', 20, netconf_session_thread, method_para2),
                            SessionTask('NETCONF', 20, netconf_session_thread, method_para3),
                            SessionTask('NETCONF', 20, netconf_session_thread, method_para4),
                            SessionTask('NETCONF', 20, netconf_session_thread, method_para5)
        ],1,12*3600)


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR, 
            format='%(asctime)s - %(threadName)s - %(levelname)s -  %(message)s',
            datefmt='%m-%d %H:%M')
    rfh = RotatingFileHandler('high_iteration_netconf_100_ro.log', maxBytes=100*1024*1024, backupCount=20, mode='w')
    rfh.setLevel(logging.CRITICAL)
    fmt = logging.Formatter('%(asctime)s - %(threadName)s - %(levelname)s -  %(message)s',
            datefmt='%m-%d %H:%M')
    rfh.setFormatter(fmt)
    logging.root.addHandler(rfh)
    main()

