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

class ConnectContext:
    def __init__(self, ip, port, user, passwd, connect_timeout=None, others={}):
        self.ip = ip
        self.port = port
        self.user = user
        self.password = passwd
        self.timeout = connect_timeout
        self.context = others

    def get(self,key):
        return self.context.get(key)

class Command:
    def __init__(self,command, verify=None, kwargs={}):
        self.command = command
        self.verify = verify
        self.kwargs = kwargs

    def getExecuteTimes(self):
        if not self.kwargs or not self.kwargs.get("repeat"):
            return 1
        else:
            return int(self.kwargs["repeat"])

    def getCommandType(self):
        if not self.kwargs or not self.kwargs.get("type"):
            return None
        else:
            return self.kwargs["type"]

    def isEval(self):
        if self.kwargs and (self.kwargs.get("eval") or self.getCommandType() == "ext"):
            return True 
        return False

    def getMode(self):
        if not self.kwargs or not self.kwargs.get("mode"):
            return None
        else:
            return self.kwargs["mode"]

    def isRead(self):
        return not self.getMode() or self.getMode() == "r"

    def isWrite(self):
        return self.getMode() and self.getMode() == "w"

    def getArgument(self, arg):
        if not self.kwargs or not self.kwargs.get(arg):
            return None
        else:
            return self.kwargs[arg]

    def getCommand(self):
        if self.isEval():
            return eval(self.command)
        else:
            return self.command


class SessionTask:
    def __init__(self, interface_type, session_number, method_parameters):
        self.interface_type = interface_type
        self.session_number = session_number
        self.method_parameters = method_parameters

class CommonInterface:
    def __init__(self):
        self.client = None

    def login(self, context):
        pass

    def get(self, command):
        pass

    def set(self, command):
        pass

    def close(self):
        if self.client:
            self.client.close()
            self.client = None

class CLIInterface(CommonInterface):

    def login(self, context):
        self.client = sclient.SSHSession(context.ip,user=context.user,passwd=context.password)
        connected, reason = self.client.connect()
        return (connected, reason)

    def get(self, command):
        result, output = self.client.sendCmd_without_connection_retry(cmd=command.getCommand())
        return (result, output)

    def set(self, command):
        result, output = self.client.sendCmd_without_connection_retry(cmd=command.getCommand())
        return (result, output)

class NetconfInterface(CommonInterface):

    def login(self, context):
        self.client = nclient.NetconfSession(context.ip,
                user = context.user,
                passwd = context.password,
                timeout = context.timeout) 
        connected, reason = self.client.connect()
        return (connected, reason) 

    def get(self, command):
        if command.getCommandType() == "rpc":
            result, output = self.client.call_rpc(rpc_content=command.getCommand())
        elif command.getCommandType() == "stream":
            result, output = self.client.create_subscription(None,"NETCONF",None,None)
            result, output = self.client.get_notification(True,
                    5 if not command.getArgument("wait") else int(command.getArgument("wait")))
        else:
            result, output = self.client.get(xpath=command.getCommand())
        return (result, output)

    def set(self, command):
        if command.getCommandType() == "rpc":
            result, output = self.client.call_rpc(rpc_content=command.getCommand())
        else:
            result, output = self.client.edit_config(config=command.getCommand(),
                dataStore="running" if ( not command.kwargs or not command.kwargs.get("target")) 
                                    else command.kwargs["target"])
        return (result, output)


class RestconfInterface(CommonInterface):

    def login(self, context):
        self.client = rclient.RestconfSession(context.ip,context.port,context.user,context.password)
        status, reason, info = self.client.connect()
        if status != 200 :
            connected = False
        else:
            connected = True
        return (connected, f"Status: {status}, Reason:{reason}, Info:{info}")        

    def get(self, command):
        result, reason, output = self.client.get(command.getCommand())
        if result <=200 and result < 300:
            r = True
        else:
            r = False
        return (r, f"Status: {result}, Reason:{reason}, Output:{output}")


    def set(self, command):
        result, reason, output = self.client.patch(command.getCommand(),
                command.getArgument("payload"))
        if result <=200 and result < 300:
            r = True
        else:
            r = False
        return (r, f"Status: {result}, Reason:{reason}, Output:{output}")


class RestconfCookieInterface(RestconfInterface):

    def login(self, context):
        self.client = rclient.RestconfCookieSession(context.ip,context.port,context.user,context.password,context.get("scheme"))
        status, reason, info = self.client.connect()
        if status != 204 :
            connected = False
        else:
            connected = True
        return (connected, f"Status: {status}, Reason:{reason}, Info:{info}")        

_buildin_nbi = {"CLI": CLIInterface, 
                "NETCONF": NetconfInterface, 
                "RESTCONF": RestconfInterface,
                "CRESTCONF": RestconfCookieInterface}


def high_iteration_run(iter_num,  connect_context, command_context, to_close=True, fail_to_retry=False, delay=0, force_delay=False):
    mythread = threading.current_thread();
    mythread.stats={"name": mythread.getName(), "fail": 0, "succ": 0, "start_time": datetime.datetime.now()}
    client = None
    connected = True
    mythread.mystop = False
    i=0
    while i < iter_num and not mythread.mystop:
        try:
            if not client:
                client = _buildin_nbi[mythread.interface_type]()
                connected, reason = client.login(connect_context)
                if not connected:
                    logger.critical(f"[{i}] -- CONNECT_ERROR:{reason}")
                    mythread.stats["fail"] += 1
            if connected:
                result = False
                output = ""
                if command_context and command_context.get("commands"):
                    commands = command_context["commands"]
                    for j in range(len(commands)):
                        command=commands[j]
                        if command.isRead():
                            logger.critical(f" [{i}:{j}] [RC] -- {command.getCommand()}")
                            for times in range(command.getExecuteTimes()):
                                if command.getCommandType() == "ext":
                                    output = command.getCommand()
                                    result = True
                                else:
                                    result, output = client.get(command)
                                logger.critical(f" [{i}:{j}] [RR]  -- {result}")
                            logger.critical(f" [{i}:{j}] [RR]  --  {output}")
                        elif command.isWrite():
                            logger.critical(f" [{i}:{j}] [WC] -- {command.getCommand()}")
                            for times in range(command.getExecuteTimes()):
                                if command.getCommandType() == "ext":
                                    output = command.getCommand()
                                    result = True
                                else:
                                    result, output = client.set(command)
                                logger.critical(f" [{i}:{j}] [WR] -- {result}")
                            logger.critical(f" [{i}:{j}] [WR] -- {output}")
                mythread.stats["succ"] += 1 
            if to_close or not connected:
                client.close()
                client = None
        except Exception as e:
            logger.exception(e)
            logger.critical(f"Error:{str(e)}")
            mythread.stats["fail"] += 1
            if not connected and client:
                client.close()
                client = None
        if not fail_to_retry or connected:
            i += 1
        if force_delay or (delay and not connected):
            time.sleep(random.randrange(int(delay)))
    if client:
        client.close()
        client=None
    mythread.stats["end_time"]=datetime.datetime.now()

def test_parallel_sessions(tasks: list, delay=0, howlong=None):
    session_threads = []
    session_id = 1
    for task in tasks:
        for i in range(task.session_number):
            th = Thread(target=high_iteration_run,
                    name=f"{task.interface_type}-{session_id}",
                    args=task.method_parameters)
            th.interface_type=task.interface_type
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
    for s in range(len(session_threads)):
        sess_th = session_threads[s]
        time1 = time.time()
        if time1 - time0 < howlong:
            logger.critical(f"join thread {sess_th.getName()} for {howlong-time1+time0} seconds")
            sess_th.join(howlong-time1+time0)
        logger.critical(f"join thread {sess_th.getName()} for stop")
        for ss in range(s,len(session_threads)):
            session_threads[ss].mystop = True
        sess_th.join()
            
    succ_times=0
    fail_times=0
    for sess_th in session_threads:
        logger.critical("{} - Failed:{} - Success:{} - Start:{} - End:{}".format(sess_th.stats["name"],
                        sess_th.stats["fail"], sess_th.stats["succ"], 
                        sess_th.stats["start_time"], sess_th.stats["end_time"]))
        fail_times += int(sess_th.stats["fail"])
        succ_times += int(sess_th.stats["succ"])
    end_time = datetime.datetime.now()
    logger.critical("Start:{} --- End:{}".format(start_time,end_time))
    logger.critical("Total: {} --- Failed: {} --- Success: {} --- Succeed Rate: {}%".format(succ_times+fail_times, fail_times, 
        succ_times, succ_times*100//(fail_times+succ_times))) 

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
    # method_para1 = (10, 'aaa.aaa.aaa.aaa', 22, 'xxx', 'xxxxxx', [Command("ls")], None, True)
    method_para1 = (1000, 'aaa.aaa.aaa.aaa', 22, 'admin0', 'xxxxxxx', [Command("show card-1-5")], None, True)
    method_para2 = (1000, 'aaa.aaa.aaa.aaa', 830, 'admin1', 'xxxxxxx', [Command("/ne/equipment/card[name='1-5']")], None, True)
    method_para3 = (1000, 'aaa.aaa.aaa.aaa', 8181, 'admin2', 'xxxxxxx', [Command("ioa-network-element:ne/equipment/card=1-5?depth=2")], None, True)
    method_para4 = (1000, 'aaa.aaa.aaa.aaa', 830, 'admin3', 'xxxxxxx', [Command("/ne/equipment/card[name='1-5']")], None, True)
    method_para5 = (1000, 'aaa.aaa.aaa.aaa', 22, 'admin4', 'xxxxxxx', [Command("show card-1-5")], None, True)
    method_para6 = (1000, 'aaa.aaa.aaa.aaa', 8181, 'admin4', 'xxxxxxx', [Command("ioa-network-element:ne/equipment/card=1-5?depth=2")], None, True)
    test_parallel_sessions([
                            SessionTask('CLI', 20,  method_para1),
                            SessionTask('NETCONF', 20,  method_para2),
                            SessionTask('RESTCONF', 20,  method_para3),
                            SessionTask('NETCONF', 20,  method_para4),
                            SessionTask('CLI', 10,  method_para5),
                            SessionTask('RESTCONF', 9, method_para6),
        ],3,360)


