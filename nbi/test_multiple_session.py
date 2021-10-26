import time
import threading
from threading import Thread
import logging
from logging.handlers import RotatingFileHandler
import datetime
import random
import nbi.gnmi.client as gclient
import nbi.netconf.client as nclient
import nbi.restconf.client as rclient
import nbi.ssh.client as sclient

logger = logging.getLogger(__name__)

class Command:
    def __init__(self,command, verify=None, kwargs={}):
        self.command = command
        self.verify = verify
        self.kwargs = kwargs

class SessionTask:
    def __init__(self, interface_type, session_number, thread_method, method_parameters):
        self.interface_type = interface_type
        self.session_number = session_number
        self.thread_method = thread_method
        self.method_parameters = method_parameters

def cli_session_thread(iter_num,ip, port, user_name, passwd, read_operations, write_operations, to_close=True, fail_to_retry=False):
    mythread = threading.current_thread();
    mythread.stats={"name": mythread.getName(), "fail": 0, "succ": 0, "start_time": datetime.datetime.now()}
    client = None
    connected = True
    mythread.mystop = False
    i = 0
    while i < iter_num and not mythread.mystop:
        try:
            if not client:
                client = sclient.SSHSession(ip,user=user_name,passwd=passwd)
                connected, reason = client.connect()
                if not connected:
                    logger.critical(f" [{i}] -- CONNECT_ERROR:{reason}")
                    mythread.stats["fail"] += 1
            if connected:
                if read_operations:
                    for read_oper in read_operations:
                        logger.critical(f" [{i}] -- {read_oper.command}")
                        result, output = client.sendCmd_without_connection_retry(cmd=read_oper.command)
                        logger.critical(f" [{i}] -- {output}")
                    mythread.stats["succ"] += 1
                if write_operations:
                    for write_oper in write_operations:
                        logger.critical(write_oper.command)
                        result, output = client.sendCmd_without_connection_retry(cmd=write_oper.command)
                    mythread.stats["succ"] += 1
            if to_close or not connected:
                client.close()
                client = None
        except Exception as e:
            logger.exception(e)
            logger.critical(f"Error:{str(e)}")
            mythread.stats["fail"] += 1
        if fail_to_retry and not connected:
            time.sleep(random.randrange(6))
        else:
            i += 1
    mythread.stats["end_time"]=datetime.datetime.now()

def netconf_session_thread(iter_num,ip, port, user_name, passwd, read_operations, write_operations, to_close=True, fail_to_retry=False):
    mythread = threading.current_thread();
    mythread.stats={"name": mythread.getName(), "fail": 0, "succ": 0, "start_time": datetime.datetime.now()}
    client = None
    connected = True
    mythread.mystop = False
    i=0
    while i < iter_num and not mythread.mystop:
        try:
            if not client:
                client = nclient.NetconfSession(ip,user=user_name,passwd=passwd,timeout=300) 
                connected, reason = client.connect()
                if not connected:
                    logger.critical(f"[{i}] -- CONNECT_ERROR:{reason}")
                    mythread.stats["fail"] += 1
            if connected:
                if read_operations:
                    for read_oper in read_operations:
                        logger.critical(f" [{i}] -- {read_oper.command}")
                        result, output = client.get(xpath=read_oper.command)
                        logger.critical(f" [{i}] -- {output}")
                    mythread.stats["succ"] += 1
                if write_operations:
                    for write_oper in write_operations:
                        logger.critical(write_oper.command)
                        result, output = client.edit_config(config=write_oper.command,
                                dataStore="running" if ( not write_oper.kwargs or not write_oper.kwargs.get("target")) 
                                else write_oper.kwargs["target"])
                        logger.critical(output)
                    mythread.stats["succ"] += 1
                if not read_operations and not write_operations:
                    mythread.stats["succ"] += 1
            if to_close or not connected:
                client.close()
                client = None
        except Exception as e:
            logger.exception(e)
            logger.critical(f"Error:{str(e)}")
            mythread.stats["fail"] += 1
        if fail_to_retry and not connected:
            time.sleep(random.randrange(6))
        else:
            i += 1
    mythread.stats["end_time"]=datetime.datetime.now()

def restconf_session_thread(iter_num,ip, port, user_name, passwd, read_operations, write_operations, to_close=True, fail_to_retry=False):
    mythread = threading.current_thread();
    mythread.stats={"name": mythread.getName(), "fail": 0, "succ": 0, "start_time": datetime.datetime.now()}
    client = None
    connected = True
    mythread.mystop = False
    i=0
    while i < iter_num and not mythread.mystop:
        try:
            if not client:
                client = rclient.RestconfSession(ip,port,user_name,passwd)
                status, reason, info = client.connect()
                if status != 200 :
                    logger.critical(f" [{i}] -- CONNECT_ERROR:{connected}-{reason}-{info}")
                    mythread.stats["fail"] += 1
                    connected = False
                else:
                    connected = True
            if connected:
                if read_operations:
                    for read_oper in read_operations:
                        logger.critical(f" [{i}] -- {read_oper.command}")
                        result, reason, output = client.get(url=read_oper.command)
                        logger.critical(f" [{i}] [R] -- {output}")
                    mythread.stats["succ"] += 1
                if write_operations:
                    for write_oper in write_operations:
                        logger.critical(write_oper.command)
                        result, reason, output = client.patch(url=write_oper.command,
                                body=write_oper.kwargs["payload"])
                        logger.critical(f" [{i}] [W] -- {result} -- {reason}")
                    mythread.stats["succ"] += 1
            if to_close or not connected:
                client.close()
                client = None
        except Exception as e:
            logger.exception(e)
            logger.critical(f"Error:{str(e)}")
            mythread.stats["fail"] += 1
        if not connected and fail_to_retry:
            time.sleep(random.randrange(6))
        else:
            i += 1
    mythread.stats["end_time"]=datetime.datetime.now()

def restconf_cookie_session_thread(iter_num,ip, port, user_name, passwd, read_operations, write_operations):
    """
        Restconf for cookies
        write_operations support patch update operation only, now
    """
    mythread = threading.current_thread();
    mythread.stats = {"name": mythread.getName(), "fail": 0, "succ": 0, "start_time": datetime.datetime.now()}
    for i in range(iter_num):
        try:
            client = rclient.RestconfCookieSession(ip,port,user_name,passwd)
            result, reason, info = client.login()
            if result != 204:
                logger.error(f"CONNECT_ERROR:{result}-{reason}-{info}")
                mythread.stats["fail"] += 1
            else:
                if read_operations:
                    for read_oper in read_operations:
                        # logger.critical(read_oper.command)
                        result, reason, output = client.get(url=read_oper.command)
                        logger.critical("result %s, iter_num read %s" % (result, i))
                    mythread.stats["succ"] += 1
                if write_operations:
                    for write_oper in write_operations:
                        result, reason, output = client.patch(url=write_oper.command,json=write_oper.kwargs.get('payload'))
                        logger.critical("result %s, iter_num write %s" % (result, i))
                    mythread.stats["succ"] += 1
            client.logout()
        except Exception as e:
            logger.debug(e)
            logger.error(f"Error:{str(e)}")
            mythread.stats["fail"] += 1
    mythread.stats["end_time"]=datetime.datetime.now()

def test_parallel_sessions(tasks: list, delay=0, howlong=None):
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

    if not howlong:
        howlong = 30*24*3600
    logger.critical(f"HOWLONG: {howlong}")

    time0 = time.time()
    for sess_th in session_threads:
        time1 = time.time()
        if time1 - time0 < howlong:
            logger.critical(f"join thread {sess_th.getName()} for {howlong-time1+time0} seconds")
            sess_th.join(howlong-time1+time0)
        logger.critical(f"join thread {sess_th.getName()} for stop")
        sess_th.mystop = True
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
    rfh.setLevel(logging.CRITICAL)
    fmt = logging.Formatter('%(asctime)s - %(threadName)s - %(levelname)s -  %(message)s',
            datefmt='%m-%d %H:%M')
    rfh.setFormatter(fmt)
    logging.root.addHandler(rfh)
    # ch = logging.StreamHandler()
    # ch.setLevel(logging.DEBUG)
    # logger.addHandler(ch)
    # method_para1 = (10, '172.29.14.151', 22, 'dci', 'Dci4523', [Command("ls")], None, True)
    method_para1 = (1000, '172.29.202.84', 22, 'admin0', 'e2e!Net4u#', [Command("show card-1-5")], None, True)
    method_para2 = (1000, '172.29.202.84', 830, 'admin1', 'e2e!Net4u#', [Command("/ne/equipment/card[name='1-5']")], None, True)
    method_para3 = (1000, '172.29.202.84', 8181, 'admin2', 'e2e!Net4u#', [Command("ioa-network-element:ne/equipment/card=1-5?depth=2")], None, True)
    method_para4 = (1000, '172.29.202.84', 830, 'admin3', 'e2e!Net4u#', [Command("/ne/equipment/card[name='1-5']")], None, True)
    method_para5 = (1000, '172.29.202.84', 22, 'admin4', 'e2e!Net4u#', [Command("show card-1-5")], None, True)
    method_para6 = (1000, '172.29.202.84', 8181, 'admin4', 'e2e!Net4u#', [Command("ioa-network-element:ne/equipment/card=1-5?depth=2")], None, True)
    test_parallel_sessions([
                            SessionTask('CLI', 20, cli_session_thread, method_para1),
                            SessionTask('NETCONF', 20, netconf_session_thread, method_para2),
                            SessionTask('RESTCONF', 20, restconf_session_thread, method_para3),
                            SessionTask('NETCONF', 20, netconf_session_thread, method_para4),
                            SessionTask('CLI', 10, cli_session_thread, method_para5),
                            SessionTask('RESTCONF', 9, restconf_session_thread, method_para6),
        ],3,360)


