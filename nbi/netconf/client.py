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
        print("to connect")


    def connect(self, timeout=100, hostkey_verify=False):

        try:
            self.establishConnection = manager.connect(host=self.ip, port=self.port, username=self.user,
                                                       password=self.passwd, timeout=self.timeout, hostkey_verify=False,
                                                       **self.kwargs)
            try:

                self.establishConnection._session.transport.set_keepalive(interval=1)

            except:
                logger.debug(e)
                logger.warning("Session Disconnected.. Keep alive expires..!!")
            return (True, "Connected")
        except Exception as e:
            logger.exception(e)
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
    netconf_obj.close()
    print(output)
