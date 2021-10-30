import time
import logging
from logging.handlers import RotatingFileHandler
from nbi.test_multiple_session import *

logger = logging.getLogger(__name__)

def main():
    method_para1 = (1000, 'ddd.ddd.ddd.ddd', 22, 'admin0', 'xxxxxxxx', [Command("show card-1-5")], None, True)
    method_para2 = (1000, 'ddd.ddd.ddd.ddd', 830, 'admin1', 'xxxxxxxx', [Command("/ne/equipment/card[name='1-5']")], None, True)
    method_para3 = (1000, 'ddd.ddd.ddd.ddd', 8181, 'admin2', 'xxxxxxxx', [Command("ioa-network-element:ne/equipment/card=1-5?depth=2")], None, True)
    method_para4 = (1000, 'ddd.ddd.ddd.ddd', 830, 'admin3', 'xxxxxxxx', [Command("/ne/equipment/card[name='1-5']")], None, True)
    method_para5 = (1000, 'ddd.ddd.ddd.ddd', 22, 'admin4', 'xxxxxxxx', [Command("show card-1-5")], None, True)
    method_para6 = (1000, 'ddd.ddd.ddd.ddd', 8181, 'admin4', 'xxxxxxxx', [Command("ioa-network-element:ne/equipment/card=1-5?depth=2")], None, True)
    test_parallel_sessions([
                            SessionTask('CLI', 20, cli_session_thread, method_para1),
                            SessionTask('NETCONF', 20, netconf_session_thread, method_para2),
                            SessionTask('RESTCONF', 20, restconf_session_thread, method_para3),
                            SessionTask('NETCONF', 20, netconf_session_thread, method_para4),
                            SessionTask('CLI', 10, cli_session_thread, method_para5),
                            SessionTask('RESTCONF', 9, restconf_session_thread, method_para6),
        ],3,3600*12)


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

