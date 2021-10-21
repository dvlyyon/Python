import paramiko
import time
import logging
from paramiko import Transport
import re

logger = logging.getLogger(__name__)


class SSHSession:
    """
        The InfnSSH class is the low-level class used to perform operations on the device thru ssh.
    """

    def __init__(self,
                 ip,
                 port=22,
                 user="secadmin",
                 passwd="Infinera1",
                 timeout=15,
                 kwargs={}):

        self.initial_prompts = ["> ","$ ","# "]
        self.ip = ip
        self.port = port
        self.user = user
        self.passwd = passwd
        self.ssh = None
        self.shell = None
        self.logger = logger
        self.login = False
        self.enable = False
        self.config = False
        self.enable = False
    

    def connect(self):

        try:

            self.ssh = paramiko.SSHClient()


            # if self.load_system_host_key!=None:
                # self.ssh.load_system_host_keys(filename=self.load_system_host_key)

            # if self.load_host_key!=None:
                # self.ssh.load_host_keys(filename=self.load_host_key)


            # if self.ssh_policy == "WARNING_POLICY":
                # self.ssh.set_missing_host_key_policy(paramiko.WarningPolicy())
            # elif self.ssh_policy == "MISSING_HOST_POLICY":
                # self.ssh.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
            # elif self.ssh_policy == "REJECT_POLICY":
                # self.ssh.set_missing_host_key_policy(paramiko.RejectPolicy())
            # else:
                # self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            try:
                self.ssh.connect(self.ip, port=self.port, username=self.user, password=self.passwd,look_for_keys=False, banner_timeout=300, auth_timeout=120)
                # self.ssh.connect(self.ip, port=self.port, username=self.user, password=self.passwd,
                                 # pkey               =   self.kwargs.get("pkey",None),
                                 # key_filename       =   self.kwargs.get("key_filename",None),
                                 # timeout            =   self.kwargs.get("timeout",None),
                                 # allow_agent        =   self.kwargs.get("allow_agent",None),
                                 # look_for_keys      =   self.kwargs.get("look_for_keys",True),
                                 # compress           =   self.kwargs.get("compress",False),
                                 # sock               =   self.kwargs.get("sock",None),
                                 # gss_auth           =   self.kwargs.get("gas_auth",False),
                                 # gss_kex            =   self.kwargs.get("gas_kex",False),
                                 # gss_deleg_creds    =   self.kwargs.get("gss_deleg_creds",True),
                                 # gss_host           =   self.kwargs.get("gss_host",None),
                                 # banner_timeout     =   self.kwargs.get("banner_timeout",None),
                                 # auth_timeout       =   self.kwargs.get("auth_timeout",None),
                                 # gss_trust_dns      =   self.kwargs.get("gss_trust_dns",True),
                                 # passphrase         =   self.kwargs.get("passphrase",None),
                                 # disabled_algorithms=   self.disable_algorithm,
                                 # )

            except Exception as e: 
                raise Exception( "SSH connection to '%s' failed:%s" % (self.ip, str(e)))

            time.sleep(5)
            ### Jira PACE-11 issue. Increasing the shell size

            self.shell = self.ssh.invoke_shell(width=99999, height=99999)
            self.shell.keep_this = self.ssh

            try:
                self.ssh.get_transport().set_keepalive(interval=1)

            except Exception as e:
                self.logger.warning("Session Disconnected.. Keep alive expires..!!")
                logger.warning(e)
                self.ssh.get_transport().active = False

            prompt_read=0
            output=''
            while prompt_read<60: # After initial connection.. reading the output buffer and checking for prompt till 60 seconds. 60 sec considered as max timeout
                output += self.read_output_buffer()
                if self.check_for_prompt(output_response=output,prompt_list=self.initial_prompts):
                    self.logger.debug("Connected successfully to '%s' via SSH" % self.ip)
                    # logger.info(output)
                    return (True, f"Connected successfully to {self.ip} via SSH")
                time.sleep(1)
                prompt_read+=1

            self.logger.debug("Connected.. but Connection prompt {} not present in NE response : {} ".format(",".join(self.initial_prompts),output))
            return (False, "Connected and Not get prompt in 1 minutes")
        except Exception as e:
            logger.exception(e)
            return (False,"SSH connection to '%s' failed:%s" % (self.ip, str(e)))

# ------------------------------------------------------------------------------------------------------------------
    def check_for_prompt(self, output_response: str, prompt_list: list, is_tl1: bool = False):
        all_prompt_list = []
        if prompt_list!=None and prompt_list !=[]:
            if not isinstance(prompt_list,list):
                all_prompt_list=[prompt_list]
            else:
                all_prompt_list = prompt_list

        if is_tl1:
            if re.search("(Copyright|COMPLD|DENY).*TL1>>", output_response, re.DOTALL) :
                return True
            else:
                return False

        for each_prompt in all_prompt_list:
            if str(output_response).endswith(each_prompt):
                logger.debug("Got the output with the Prompt Ending with : '{}'".format(each_prompt))
                return True
        return False

# ----------------------------------------------------------------------------------------------------------------------

    def read_output_buffer(self):

        output = ''
        if self.shell.recv_ready():
            bufferLen = len(self.shell.in_buffer)
            if bufferLen > 0:
                response = self.shell.recv(bufferLen)
                output = output + self.removeANSIescapeSequence(response)

        return output

# ----------------------------------------------------------------------------------------------------------------

    def check_connectivity_and_reconnect(self):

        try:

            if self.ssh.get_transport().is_active() == False:
                self.logger.debug('Looks like NE connectivity went down.. Let me wait for 15 seconds and will try connecting back...')
                time.sleep(15)
                self.connect()

            return True

        except Exception as e:

            self.logger.warning(' NE didnt connected after 15 seconds... Please check.. ')
            self.logger.warning(e)
            return False

    def get_connection_status(self):

        return self.ssh.get_transport().is_active()

    def sendCmd(self, cmd, delay=2, prompt=None, carriage_return="\r\n", is_tl1=False):
        """
            This function is used to send command and receive the output
        """
        output = ''

        try:
            #operations-->manager-->cli---->ssh(Reconnect and clear the buffer)
            if self.check_connectivity_and_reconnect():
                try:
                    if self.shell.send_ready():
                        logger.debug("clearing the output buffer... just in case..")
                        self.read_output_buffer() #Logic to ensuring the socket buffer is cleaned up before firing next command
                        self.shell.send('%s%s' % (cmd,carriage_return))
                        time.sleep(1)
                    else:
                        self.logger.error("Paramiko send channel not ready")
                        return (False, "Paramiko send channel not ready")

                except Exception as e:
                    # Somekind of socket error
                    # Re establish the shell
                    self.logger.debug(e)
                    self.shell = self.ssh.invoke_shell()
                    self.shell.keep_this = self.ssh
                    self.read_output_buffer() #Logic to ensuring the socket buffer is cleaned up before firing next command
                    self.shell.send('%s%s' % (cmd, carriage_return))
                    time.sleep(1)

                # self.logger.debug("Entered: %s" % cmd)

                sleep_time = 0

                while sleep_time<delay:
                    if self.shell.recv_ready():
                        # print("reading data from socket..!")
                        bufferLen = len(self.shell.in_buffer) # Paramiko buffer
                        response = self.shell.recv(bufferLen)
                        # logger.debug("####response=%s" % response)
                        output = output + self.removeANSIescapeSequence(response)
                        if self.check_for_prompt(output_response=output,prompt_list=prompt,is_tl1=is_tl1):
                            logger.debug("Received output till the prompt given..!! command completed successfully..!!")
                            break
                        time.sleep(1)
                        sleep_time += 1
                    else:
                        print("socket not ready.. wait for 1 sec")
                        time.sleep(1)
                        sleep_time += 1

                if str(output).startswith(cmd):
                    output = "\n".join(output.split(carriage_return)[1:])
                # self.logger.debug('After Removing ANSIescapeSquence=%s' % output)

                return (True, output)

            else:

                self.logger.debug('Session seems to be closed...')

                return (False, "Session seems to be closed")

        except Exception as exe:
            logger.warning(exe)
            return (False, str(exe))

    def sendCmd_without_connection_retry(self, cmd, delay=2,prompt=None):
        """
            This function is used to send command and receive the output
        """
        output = ''

        try:
            if self.shell.send_ready():
                self.read_output_buffer()
                self.shell.send('%s\n' % cmd)
                time.sleep(delay)
            else:
                self.logger.debug("Paramiko send channel not ready")
                return (False, "Paramiko send channel not ready")

        except Exception as e:
            self.logger.debug(e)
            self.shell = self.ssh.invoke_shell()
            self.shell.keep_this = self.ssh
            self.read_output_buffer()
            self.shell.send('%s\n\n' % cmd)

        # self.logger.info("Entered: %s" % cmd)

        sleep_time = 0
        while sleep_time < delay:
            if self.shell.recv_ready():
                logger.debug("reading data from socket..!")
                bufferLen = len(self.shell.in_buffer)  # Paramiko buffer
                response = self.shell.recv(bufferLen)
                # logger.info("####response=%s" % response)
                output = output + self.removeANSIescapeSequence(response)
                if self.check_for_prompt(output_response=output, prompt_list=prompt):
                    logger.debug("Received output till the prompt given..!! command completed successfully..!!")
                    break
                time.sleep(1)
                sleep_time += 1
            else:
                logger.debug("socket not ready.. wait for 1 sec")
                time.sleep(1)
                sleep_time += 1

        self.logger.debug('After Removing ANSIescapeSquence=%s' % output)

        return (True,output)

    def removeANSIescapeSequence(self, text):
        text = text.decode('utf-8', errors="ignore")
        ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
        result = ansi_escape.sub('', text)
        return result

    def close_session(self,):

        return self.close()

    def close(self):
        '''
            This function is used to close the telnet connect
        '''
        if self.ssh:
            self.ssh.close()

if __name__ == "__main__":
    ssh_obj = SSHSession(ip='172.29.202.84',user='administrator',passwd='e2e!Net4u#')
    ssh_obj.connect()
    output = ssh_obj.sendCmd_without_connection_retry(cmd="show inventory", delay=2)
    print(output)

