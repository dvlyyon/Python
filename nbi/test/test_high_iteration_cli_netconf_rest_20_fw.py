import time
import logging
from logging.handlers import RotatingFileHandler
from nbi.test_high_iteration_framework import *

logger = logging.getLogger(__name__)

def main():
    ports=[20,20,830,8181,8181]
    ip='aaa.aaa.aaa.aaa'
    user='admin0'
    passwd='xxxxxxxx'
    connect_contexts = [ConnectContext(ip,p,user,passwd) for p in ports]
    commands=[
            Command("show card-1-5"),
            Command("show session"),
            Command("/ne/equipment/card[name='1-5']"),
            Command("ioa-network-element:ne/equipment/card=1-5?depth=2"),
            Command("ioa-network-element:ne/equipment/card=1-5?depth=2")
            ]
    method_paras=[]
    for i in range(len(ports)):
        method_paras.append((1000,connect_contexts[i],{"commands": [commands[i]]}, True, False, 3))
    iftypes = ['CLI','CLI','NETCONF','RESTCONF','CRESTCONF']
    ssnums = [3,2,10,2,3]
    sessions =[]
    for i in range(len(iftypes)):
        sessions.append(SessionTask(iftypes[i],ssnums[i],method_paras[i]))
    test_parallel_sessions(sessions,3,12*3600)


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR, 
            format='%(asctime)s - %(threadName)s - %(levelname)s -  %(message)s',
            datefmt='%m-%d %H:%M')
    rfh = RotatingFileHandler('high_iteration_cli_netconf_rest_20_fw.log', maxBytes=100*1024*1024, backupCount=20, mode='w')
    rfh.setLevel(logging.CRITICAL)
    fmt = logging.Formatter('%(asctime)s - %(threadName)s - %(levelname)s -  %(message)s',
            datefmt='%m-%d %H:%M')
    rfh.setFormatter(fmt)
    logging.root.addHandler(rfh)
    main()

