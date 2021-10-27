import re
import logging

#from .lib.CreateXml import CreateXml
from ncclient import manager, xml_
from ncclient.operations import RPCError, MissingCapabilityError, RPCReply, GetReply
import os
import subprocess

logger = logging.getLogger(__name__)
import time

ERROR_MESSAGE = "NETCONF FAILURE:"


class NetconfSession:
    namespace_details = None

    def __init__(self, ip, user, passwd, port=830, timeout=15, kwargs={}):
        self.ip = ip
        self.port = port
        self.user= user
        self.passwd = passwd
        self.kwargs = kwargs
        self.timeout = timeout
        if "disable_algorithm" in self.kwargs:
            self.kwargs.pop("disable_algorithm")
        HOST = self.ip
        USER = self.user
        PASS = self.passwd
        PORT = port


    def connect(self, timeout=100, hostkey_verify=False):

        try:
            self.establishConnection = manager.connect(host=self.ip, port=self.port, username=self.user,
                                                       password=self.passwd, timeout=self.timeout, hostkey_verify=False,
                                                       **self.kwargs)
            try:

                self.establishConnection._session.transport.set_keepalive(interval=1)

            except:
                logger.exception(e)
                logger.warning("Session Disconnected.. Keep alive expires..!!")
            return (True, "Connected")
        except Exception as e:
            logger.debug(e)
            return (False,str(e))

    def check_connectivity(self):

        try:

            if self.establishConnection._session.connected == False:
                logger.warning(
                    'Looks like NE is down.. Lets wait for 10 sec.. may be a network glitch.. or NE Rebooted... :)')

                time.sleep(10)

                self.connect()

        except Exception as e:

            logger.warning("NE didnt connected even after 10 seconds.. looks like some crash.. please check logs")

    def get(self, xpath=None, xml=None, nameSpace=None, with_defaults=None):

        if (xpath and xml) or not (xpath or xml):
            return "One and only one of XPATH and XML must be provided"

        output = None

        if xpath != None:
            inputQuery = xpath
            inputType = 'xpath'
        else:
            inputQuery = xml
            inputType = 'subtree'

        try:

            self.check_connectivity()
            logger.debug(inputQuery)
            output = self.establishConnection.get((inputType, inputQuery), with_defaults=with_defaults).data_xml

            return (True, output)

        except RPCError as exception:

            logger.debug("RPC Error Occured %s", exception)
            output = exception

        except Exception as e:

            logger.debug("Exception Occured %s", e)
            output = e

        return (False, str(output))

    def edit_config(self, config, dataStore, default_operation=None, test_option=None, error_option=None):

        if config == None:
            return f"Please provide config parameter!!!"

        editConfig = config 
        result = True
        output = None

        try:

            self.check_connectivity()
            logger.debug(editConfig)
            output = self.establishConnection.edit_config(target=dataStore,
                                                          config=editConfig,
                                                          default_operation=default_operation,
                                                          test_option=test_option,
                                                          error_option=error_option)
        except RPCError as exception:

            logger.exception(exception)
            output = exception
            result = False

        except Exception as e:

            logger.exception("Exception Occured %s", e)
            output = e
            result = False

        return (result, str(output))

    def call_rpc(self, rpc_content ):

        output = None
        try:

            if rpc_content == None: 
                return  (False, "PLEASE provide rpc conntect with parameter rpc_content")
            self.check_connectivity()
            output = self.establishConnection.dispatch(rpc_command=xml_.to_ele(rpc_content))
            return (True, output)                                                                                                  

        except RPCError as exception:                                                                        

            logger.exception(exception)           
            return (False, str(exception))                                                                           


    def create_subscription(self, filter, stream_name, start_time, stop_time):

        output = None
        try:

            self.check_connectivity()
            output = self.establishConnection.create_subscription(filter=filter, stream_name=stream_name,
                                                                  start_time=start_time, stop_time=stop_time)

        except RPCError as exception:

            logger.exception(exception)
            output = exception
            return (False, str(output))

        except Exception as exception:

            logger.exception(exception)
            output = exception
            return (False, str(output))

        return (True, output)

    def get_notification(self, block, timeout):

        notification = []

        try:
            while (True):
                self.check_connectivity()
                output = self.establishConnection.take_notification(block=block, timeout=timeout)
                if output == None:
                    break
                else:
                    notification.append(output.notification_xml)

        except RPCError as exception:
            logger.exception(exception)
            return (False, str(exception))

        except Exception as e:
            logger.exception(e)
            return (False, str(e))

        return (True, notification)

    def close(self):

        output = None

        try:

            if self.establishConnection._session.connected == True:
                output = self.establishConnection.close_session()

        except RPCError as exception:
            logger.debug("RPC Error Occured when close session: %s", exception)
            output = exception

        except Exception as exception:
            logger.debug("Exception Occured when close session: ....")
            logger.debug(exception)
            output = exception

        return output


if __name__ == "__main__":
    netconf_obj = NetconfSession(ip='172.29.202.84',user='administrator',passwd='e2e!Net4u#')
    netconf_obj.connect()
    output = netconf_obj.get(xpath="/ne/equipment/card[name='1-5']")
    print(output)
    print(netconf_obj.edit_config(config="""
        <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <ne xmlns="http://infinera.com/yang/ioa/ne" xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
                <label>Changed by Netconf</label>
            </ne>
        </config>""", dataStore="running"))
    print(netconf_obj.call_rpc("""
        <get-pm xmlns="http://infinera.com/yang/ioa/pm" xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
            <data-type>real-time</data-type>
        </get-pm>"""))
    print(netconf_obj.get(xpath="/alarms/current-alarms"))

    print(netconf_obj.create_subscription(None,"NETCONF",None,None))
    print(netconf_obj.get_notification(block=1024,timeout=5))
    netconf_obj.close()
