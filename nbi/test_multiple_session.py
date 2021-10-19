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
        client = sclient.SSHSession(ip,user=user_name,passwd=passwd)
        if read_operations:
            for read_oper in read_operations:
                logger.info(read_oper.command)
                output = client.sendCmd_without_connection_retry(cmd=read_oper.command)
                logger.info(output)
        if write_operations:
            for write_oper in write_operations:
                logger.info(write_oper.command)
                output = client.sendCmd_without_connection_retry(cmd=write_oper.command)
        client.close()




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
    method_para1 = (1000, '172.29.202.84', 22, 'admin0', 'e2e!Net4u#', [Command("show card-1-5")], None)
    method_para2 = (1000, '172.29.202.84', 22, 'admin1', 'e2e!Net4u#', [Command("show card-1-5")], None)
    method_para3 = (1000, '172.29.202.84', 22, 'admin2', 'e2e!Net4u#', [Command("show card-1-5")], None)
    method_para4 = (1000, '172.29.202.84', 22, 'admin3', 'e2e!Net4u#', [Command("show card-1-5")], None)
    method_para5 = (1000, '172.29.202.84', 22, 'admin4', 'e2e!Net4u#', [Command("show card-1-5")], None)
    test_parallel_sessions([SessionTask('CLI', 20, cli_session_thread, method_para1),
                            SessionTask('CLI', 20, cli_session_thread, method_para2),
                            SessionTask('CLI', 20, cli_session_thread, method_para3),
                            SessionTask('CLI', 20, cli_session_thread, method_para4),
                            SessionTask('CLI', 20, cli_session_thread, method_para5),
        ])


