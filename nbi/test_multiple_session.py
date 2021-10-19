import time
from threading import Thread
import logging
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

def cli_session_thread(iter_num,ip, port, user_name, passwd, read_operations, write_operations):
    for i in range(iter_num):
        try:
            client = sclient.SSHSession(ip,user=user_name,passwd=passwd)
            result, reason = client.connect()
            if not result:
                logger.error(f"CONNECT_ERROR:{reason}")
            else:
                if read_operations:
                    for read_oper in read_operations:
                        logger.info(read_oper.command)
                        result, output = client.sendCmd_without_connection_retry(cmd=read_oper.command)
                        logger.info(output)
                if write_operations:
                    for write_oper in write_operations:
                        logger.info(write_oper.command)
                        result, output = client.sendCmd_without_connection_retry(cmd=write_oper.command)
            client.close()
        except Exception as e:
            logger.debug(e)
            logger.error(f"Error:{str(e)}")

def netconf_session_thread(iter_num,ip, port, user_name, passwd, read_operations, write_operations):
    for i in range(iter_num):
        try:
            client = nclient.NetconfSession(ip,user=user_name,passwd=passwd)
            result, reason = client.connect()
            if not result:
                logger.error(f"CONNECT_ERROR:{reason}")
            else:
                if read_operations:
                    for read_oper in read_operations:
                        logger.info(read_oper.command)
                        result, output = client.get(xpath=read_oper.command)
                        logger.info(output)
                if write_operations:
                    for write_oper in write_operations:
                        logger.info(write_oper.command)
#                        result, output = client.sendCmd_without_connection_retry(cmd=write_oper.command)
            client.close()
        except Exception as e:
            logger.debug(e)
            logger.error(f"Error:{str(e)}")

def restconf_session_thread(iter_num,ip, port, user_name, passwd, read_operations, write_operations):
    for i in range(iter_num):
        try:
            client = rclient.RestconfSession(ip,port,user_name,passwd)
            result, reason, info = client.connect()
            if result != 200 :
                logger.error(f"CONNECT_ERROR:{result}-{reason}-{info}")
            else:
                if read_operations:
                    for read_oper in read_operations:
                        logger.info(read_oper.command)
                        result, reason, output = client.get(url=read_oper.command)
                        logger.info(output)
                if write_operations:
                    pass
                    # for write_oper in write_operations:
                        # logger.info(write_oper.command)
                        # result, output = client.sendCmd_without_connection_retry(cmd=write_oper.command)
            client.close()
        except Exception as e:
            logger.debug(e)
            logger.error(f"Error:{str(e)}")

def test_parallel_sessions(tasks: list):
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
    for sess_th in session_threads:
        sess_th.start()

    time.sleep(120)

    for sess_th in session_threads:
        sess_th.join()
    logger.critical(datetime.datetime.now())

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, 
            format='%(asctime)s - %(threadName)s - %(levelname)s -  %(message)s',
            datefmt='%m-%d %H:%M',
            filename='myapp.log',
                    filemode='w')
    # ch = logging.StreamHandler()
    # ch.setLevel(logging.DEBUG)
    # logger.addHandler(ch)
    #method_para1 = (10, '172.29.202.84', 22, 'admin0', 'e2e!Net4u#', [Command("show card-1-5")], None)
    #method_para2 = (10, '172.29.202.84', 22, 'admin1', 'e2e!Net4u#', [Command("/ne/equipment/card[name='1-5']")], None)
    method_para3 = (10, '172.29.202.84', 8181, 'admin2', 'e2e!Net4u#', [Command("ioa-network-element:ne/equipment/card")], None)
    # method_para4 = (10, '172.29.202.84', 22, 'admin3', 'e2e!Net4u#', [Command("show card-1-5")], None)
    # method_para5 = (10, '172.29.202.84', 22, 'admin4', 'e2e!Net4u#', [Command("show card-1-5")], None)
    test_parallel_sessions([
                            # SessionTask('CLI', 20, cli_session_thread, method_para1),
                            # SessionTask('NETCONF', 20, netconf_session_thread, method_para2),
                            SessionTask('RESTCONF', 20, restconf_session_thread, method_para3),
                            # SessionTask('CLI', 20, cli_session_thread, method_para4),
                            # SessionTask('CLI', 20, cli_session_thread, method_para5),
        ])


