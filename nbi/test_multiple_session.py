import time
import threading
from threading import Thread
import logging
from logging.handlers import RotatingFileHandler
import datetime
import nbi.gnmi.client as gclient
import nbi.netconf.client as nclient
import nbi.restconf.client as rclient
import nbi.ssh.client as sclient

logger = logging.getLogger(__name__)

class Command:
    def __init__(self,command, verify=None):
        self.command = command
        self.verify = verify

class SessionTask:
    def __init__(self, interface_type, session_number, thread_method, method_parameters):
        self.interface_type = interface_type
        self.session_number = session_number
        self.thread_method = thread_method
        self.method_parameters = method_parameters

def cli_session_thread(iter_num,ip, port, user_name, passwd, read_operations, write_operations, to_close):
    mythread = threading.current_thread();
    mythread.stats={"name": mythread.getName(), "fail": 0, "succ": 0, "start_time": datetime.datetime.now()}
    client = None
    connected = True
    for i in range(iter_num):
        try:
            if not client:
                client = sclient.SSHSession(ip,user=user_name,passwd=passwd)
                connected, reason = client.connect()
                if not connected:
                    logger.error(f"CONNECT_ERROR:{reason}")
                    mythread.stats["fail"] += 1
            if connected:
                if read_operations:
                    for read_oper in read_operations:
                        logger.critical(read_oper.command)
                        result, output = client.sendCmd_without_connection_retry(cmd=read_oper.command)
                        logger.critical(output)
                    mythread.stats["succ"] += 1
                if write_operations:
                    for write_oper in write_operations:
                        logger.critical(write_oper.command)
                        result, output = client.sendCmd_without_connection_retry(cmd=write_oper.command)
                    mythread.stats["succ"] += 1
            if to_close:
                client.close()
                client = None
        except Exception as e:
            logger.debug(e)
            logger.error(f"Error:{str(e)}")
            mythread.stats["fail"] += 1
    mythread.stats["end_time"]=datetime.datetime.now()

def netconf_session_thread(iter_num,ip, port, user_name, passwd, read_operations, write_operations, to_close):
    mythread = threading.current_thread();
    mythread.stats={"name": mythread.getName(), "fail": 0, "succ": 0, "start_time": datetime.datetime.now()}
    client = None
    connected = True
    for i in range(iter_num):
        try:
            if not client:
                client = nclient.NetconfSession(ip,user=user_name,passwd=passwd)
                connected, reason = client.connect()
                if not connected:
                    logger.error(f"CONNECT_ERROR:{reason}")
                    mythread.stats["fail"] += 1
            if connected:
                if read_operations:
                    for read_oper in read_operations:
                        logger.critical(read_oper.command)
                        result, output = client.get(xpath=read_oper.command)
                        logger.critical(output)
                    mythread.stats["succ"] += 1
                if write_operations:
                    for write_oper in write_operations:
                        logger.critical(write_oper.command)
#                        result, output = client.sendCmd_without_connection_retry(cmd=write_oper.command)
                    mythread.stats["succ"] += 1
            if to_close:
                client.close()
                client = None
        except Exception as e:
            logger.debug(e)
            logger.error(f"Error:{str(e)}")
            mythread.stats["fail"] += 1
    mythread.stats["end_time"]=datetime.datetime.now()

def restconf_session_thread(iter_num,ip, port, user_name, passwd, read_operations, write_operations, to_close):
    mythread = threading.current_thread();
    mythread.stats={"name": mythread.getName(), "fail": 0, "succ": 0, "start_time": datetime.datetime.now()}
    client = None
    connected = True
    for i in range(iter_num):
        try:
            if not client:
                client = rclient.RestconfSession(ip,port,user_name,passwd)
                connected, reason, info = client.connect()
                if connected != 200 :
                    logger.error(f"CONNECT_ERROR:{result}-{reason}-{info}")
                    mythread.stats["fail"] += 1
            if connected:
                if read_operations:
                    for read_oper in read_operations:
                        logger.critical(read_oper.command)
                        result, reason, output = client.get(url=read_oper.command)
                        logger.critical(output)
                    mythread.stats["succ"] += 1
                if write_operations:
                    pass
                    # for write_oper in write_operations:
                        # logger.critical(write_oper.command)
                        # result, output = client.sendCmd_without_connection_retry(cmd=write_oper.command)
                    mythread.stats["succ"] += 1
            if to_close:
                client.close()
                client = None
        except Exception as e:
            logger.debug(e)
            logger.error(f"Error:{str(e)}")
            mythread.stats["fail"] += 1
    mythread.stats["end_time"]=datetime.datetime.now()

def test_parallel_sessions(tasks: list, delay=0):
    session_threads = []
    session_id = 1
    for task in tasks:
        for i in range(task.session_number):
            th = Thread(target=task.thread_method,
                    name=f"{task.interface_type}-{session_id}",
                    args=task.method_parameters)
            session_threads.append(th)
            session_id += 1

    logger.critical(datetime.datetime.now())
    start_time = datetime.datetime.now()
    for sess_th in session_threads:
        sess_th.start()
        time.sleep(delay)

    time.sleep(120)

    for sess_th in session_threads:
        sess_th.join()

    for sess_th in session_threads:
        logger.critical("{} - Failed:{} - Success:{} - Start:{} - End:{}".format(sess_th.stats["name"],
                        sess_th.stats["fail"], sess_th.stats["succ"], 
                        sess_th.stats["start_time"], sess_th.stats["end_time"]))
    end_time = datetime.datetime.now()
    logger.critical("Start:{} --- End:{}".format(start_time,end_time))

if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR, 
            format='%(asctime)s - %(threadName)s - %(levelname)s -  %(message)s',
            datefmt='%m-%d %H:%M')
    rfh = RotatingFileHandler('myapp.log', maxBytes=100*1024*1024, backupCount=20, mode='w')
    rfh.setLevel(logging.ERROR)
    fmt = logging.Formatter('%(asctime)s - %(threadName)s - %(levelname)s -  %(message)s',
            datefmt='%m-%d %H:%M')
    rfh.setFormatter(fmt)
    logging.root.addHandler(rfh)
    # ch = logging.StreamHandler()
    # ch.setLevel(logging.DEBUG)
    # logger.addHandler(ch)
    method_para1 = (1100, '172.29.202.84', 22, 'admin0', 'e2e!Net4u#', [Command("show card-1-5")], None, True)
    method_para2 = (1100, '172.29.202.84', 830, 'admin1', 'e2e!Net4u#', [Command("/ne/equipment/card[name='1-5']")], None, True)
    method_para3 = (1100, '172.29.202.84', 8181, 'admin2', 'e2e!Net4u#', [Command("ioa-network-element:ne/equipment/card=1-5?depth=2")], None, True)
    # method_para4 = (10, '172.29.202.84', 22, 'admin3', 'e2e!Net4u#', [Command("show card-1-5")], None)
    # method_para5 = (10, '172.29.202.84', 22, 'admin4', 'e2e!Net4u#', [Command("show card-1-5")], None)
    test_parallel_sessions([
                            SessionTask('CLI', 30, cli_session_thread, method_para1),
                            SessionTask('NETCONF', 40, netconf_session_thread, method_para2),
                            SessionTask('RESTCONF', 30, restconf_session_thread, method_para3),
                            # SessionTask('CLI', 20, cli_session_thread, method_para4),
                            # SessionTask('CLI', 20, cli_session_thread, method_para5),
        ],5)


