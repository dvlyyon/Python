import time
import logging
from logging.handlers import RotatingFileHandler
from nbi.test_multiple_session import *

logger = logging.getLogger(__name__)

def main():
    get_pm = """
        <get-pm xmlns="http://infinera.com/yang/ioa/pm" xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
            <data-type>real-time</data-type>
        </get-pm> """

    method_para1 = (1000, 'aaa.aaa.aaa.aaa', 830, 'radiustest6', 'Radius12', [
                                                                         Command(command="/alarms/current-alarms", kwargs={"repeat": 2}),
                                                                         Command(command=get_pm,kwargs = {"repeat" :2, "type": "rpc"}),
                                                                         Command(command="NETCONF",kwargs = {"type": "stream", "stream_timeout":5})
                                                                        ], 
                   None, 
                   True,True)
    method_para2 = (1000, 'aaa.aaa.aaa.aaa', 830, 'radiustest8', 'Radius123', [
                                                                         Command(command="/alarms/current-alarms", kwargs={"repeat": 2}),
                                                                         Command(command=get_pm,kwargs = {"repeat" :2, "type": "rpc"}),
                                                                         Command(command="NETCONF",kwargs = {"type": "stream", "stream_timeout":5})
                                                                        ], 
                   None, 
                   True,True)

    test_parallel_sessions([
                            SessionTask('NETCONF', 10, netconf_session_thread, method_para1),
                            SessionTask('NETCONF', 10, netconf_session_thread, method_para2)
        ],3,12*3600)


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR, 
            format='%(asctime)s - %(threadName)s - %(levelname)s -  %(message)s',
            datefmt='%m-%d %H:%M')
    rfh = RotatingFileHandler('netconf_20_radius_high_iteration_poll.log', maxBytes=100*1024*1024, backupCount=20, mode='w')
    rfh.setLevel(logging.CRITICAL)
    fmt = logging.Formatter('%(asctime)s - %(threadName)s - %(levelname)s -  %(message)s',
            datefmt='%m-%d %H:%M')
    rfh.setFormatter(fmt)
    logging.root.addHandler(rfh)
    main()

