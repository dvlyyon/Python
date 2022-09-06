import grpc
import logging
import time
from queue import ( Queue, Empty )
from .Auto_Gen_Files import gnmi_pb2, gnmi_pb2_grpc
from ..gnmi_enum import *

logger = logging.getLogger(__name__)

from threading import Thread



STREAM = 0
ONCE = 1
POLL = 2

class gNMISession:

    def __init__(self, ipAddress,gnmi_port,username,password,
            certificate_path, ca_cert, client_cert, client_key,
            ssl_target_name_override='localhost',secure_connection_type=True):

        self.ipAddress                  =   ipAddress
        self.username                   =   username
        self.password                   =   password
        self.gnmi_port                  =   gnmi_port
        self.certificate_path           =   certificate_path
        self.ssl_target_name_override   =   ssl_target_name_override
        self.secure_connection_type     =   secure_connection_type
        self.credentials                =   [('username', username), ('password', password)]
        self.ca_certificate             =   self.certificate_path + '/' + ca_cert 
        self.client_certificate         =   self.certificate_path + '/' + client_cert if client_cert else None
        self.clientKey                  =   self.certificate_path + '/' + client_key if client_key else None
        self.channel                    =   None
        self.telemetry_data_dict        = {}
        self.subscribe_requests         = {}
        self.channel_state              = True
        self.__establish_channel()

    def __establish_channel(self):


        try:

            if self.secure_connection_type:

                logger.info("In Secure Connection....")
                ca_cert = open(self.ca_certificate,mode='rb').read()
                client_key = open(self.clientKey, mode='rb').read() if self.clientKey else None
                client_cert = open(self.client_certificate, mode='rb').read() if self.client_certificate else None
                cred = grpc.ssl_channel_credentials(ca_cert,client_key,client_cert)
                target_override=[]
                if self.ssl_target_name_override !=None:
                    target_override.append(('grpc.ssl_target_name_override', self.ssl_target_name_override,))
                self.channel = grpc.secure_channel(self.ipAddress+":"+str(self.gnmi_port), cred,target_override)

            else: #insecure connection

                logger.info('Establishing Insecure Connection...')
                self.channel = grpc.insecure_channel(self.ipAddress + ":"+str(self.gnmi_port))

            self.session = gnmi_pb2_grpc.gNMIStub(self.channel)

        except Exception as e:
            # logger.debug('Not able to Establish GRPC connection..',e)
            raise Exception ('Not able to Establish GRPC connection..:%s'%str(e))
            # pytest.evaluate(False)


    def is_channel_active(self):

        return self.channel._connectivity_state


    def __check_channel_Connectivity(self):

        if self.channel_state == False :

            logger.info('Looks like channel went down...!!! Re-establishing in 10 seconds..')
            
            time.sleep(10)

            try:

                self.__establish_channel()

            except Exception as e :

                logger.debug('Couldnt able to establish the session... !!!')

                logger.debug(e)

                return False

        return True

    def close_channel(self):

        '''
        Close channel API to close the session established..

        :return: None

        @Author : rsadasivam@infinera.com

        '''

        logger.info('Closing GRPC channel....')

        try:
            self.channel._close()
            self.channel_state = False

        except Exception as e:

            logger.debug('Exception occured while closing the channel..')


    def capabilities(self):

        '''

        GPRC Capability request API to get the GRPC capabilities

        :return: returns GRPC capabilities reponse

        @Author : rsadasivam@infinera.com

        '''

        try:

            if self.__check_channel_Connectivity():

                message = gnmi_pb2.CapabilityRequest()
                response = self.session.Capabilities(message,metadata=self.credentials)
                logger.info(str(response))
                return str(response)

            else:

                logger.debug('Channel seems to be down.. !!')

        except Exception as e:

            logger.debug('Exception Occured !!')
            logger.debug(e)
            return e


    def poll_subscription(self,subscription_id):

        try:

            request = gnmi_pb2.SubscribeRequest(poll=gnmi_pb2.Poll())

            if not self.subscribe_requests[subscription_id]:
                return "Please send subscribe RPC before poll"

            self.subscribe_requests[subscription_id].put(request)

            time.sleep(2)

            return "OK"

        except Exception as exe:

            logger.debug(exe)
            return f"Exception:{exe}"



    def subscribe(self, subscription_list, mode, prefix_xpath=None, use_aliases=True,
                     qos=None, allow_aggregation=False, use_models=None, updates_only=None,
                     encoding=gnmi_pb2.JSON_IETF, poll=None, aliases=None,subscription_id=None):

        try:

            if self.__check_channel_Connectivity():

                subscriptions = []

                logger.debug(subscription_list)
                for s in subscription_list:
                    obj = SubscriptionMessage(xpath=s.get(GnmiSubscriptionKey.PATH),
                                              subscription_mode=s.get(GnmiSubscriptionKey.MODE),
                                              sample_interval=s.get(GnmiSubscriptionKey.SAMPLE_INTERVAL, 0),
                                              suppress_redundant=s.get(GnmiSubscriptionKey.SUPPRESS_REDUNDANT, False),
                                              heartbeat_interval=s.get(GnmiSubscriptionKey.HEARTBEAT_INTERVAL, 0))

                    subscriptions.append(obj)

                subs = [sub.sub for sub in subscriptions]
                logger.debug(subs)

                prefix = None

                if prefix_xpath is not None:

                    prefix = gnmi_pb2.Path(elem=gNMISession.xpath_to_Path_Element(xpath=prefix_xpath))

                request = gnmi_pb2.SubscribeRequest(subscribe=gnmi_pb2.SubscriptionList(subscription=subs,
                        prefix =prefix,
                        mode=mode.value,
                        use_aliases=False,
                        qos=qos,
                        allow_aggregation=False,
                        use_models=use_models,
                        updates_only=updates_only,
                        encoding=encoding.value,))
                logger.info(request)
                iterator_queue = Queue()
                iterator_queue.put(request)
                self.subscribe_requests[subscription_id] = iterator_queue
                request_iterator = iter(iterator_queue.get,None)
                self.response_object =  self.session.Subscribe(request_iterator, metadata=self.credentials)
                logger.info(self.response_object)
                Thread(target=self.read_iterator_to_list,args=(self.response_object,subscription_id,)).start()
                time.sleep(2)
                return self.response_object

            else:
                logger.debug('Channel seems to be down.. !!')


        except Exception as e:
            logger.debug(e)


    def read_iterator_to_list(self,response_iterator,subscription_id):

        try:

            for each_item in response_iterator:

                logger.info(each_item)

                if subscription_id not in self.telemetry_data_dict.keys():
                    self.telemetry_data_dict[subscription_id] = Queue()

                self.telemetry_data_dict.get(subscription_id).put(str(each_item))


        except Exception as e:

            logger.debug(e)

            if subscription_id in self.telemetry_data_dict.keys():
                self.telemetry_data_dict.get(subscription_id).put(str(e))

            else:
                self.telemetry_data_dict[subscription_id] = Queue()
                self.telemetry_data_dict[subscription_id].put([str(e)])
                
            
            self.channel_state = False



    # def __rpc_stream(self, method, request):

        # self.iterator_queue.put(request)
        # request_iterator = iter(self.iterator_queue.get,None)
        # logger.info(request)
        # return method(request_iterator, None, metadata=self.credentials)




    @staticmethod
    def xpath_to_Path_Element(xpath):

        '''
        Static API to form Path Element object as per the GNMI.proto from the Xpath mentioned in the subscription list..

        :param xpath: XPATH to subscribe the object
        :param namespace: XM namespace
        :return: returns path element as per GNMI.proto

        @Author : rsadasivam@infinera.com

        '''

        mypath = []

        try:

            if xpath!=None:
                #/pm/real-time-pm-data/real-time-pm[AID=*][parameter=fan-speed]

                for each_Element in xpath.split('/')[1:]:
                    all_keys = {}
                    if str(each_Element).find('[') != -1:
                        name = str(each_Element).split('[')[0]
                        for each_leaf in str(each_Element).split("[")[1:]:
                            each_leaf = "[{}".format(each_leaf)
                            all_keys[str(each_leaf.split('[')[1].split('=')[0])]= str(each_leaf.split('[')[1].split('=')[1].split(']')[0]).replace('%(','[').replace(')%',']').replace('||','/').replace('::','=')
                        mypath.append(gnmi_pb2.PathElem(name=str(name), key=all_keys))

                    else:
                        name = str(each_Element)
                        key = None

                        mypath.append(gnmi_pb2.PathElem(name=str(name), key=key))

        except Exception as exe:

            logger.debug("XPATH Parsing failed..!! Please check the input XPATH>.")
            logger.debug(exe)

        return mypath


    def telemetry_data(self,subscription_id):


        try:

            data = []

            if subscription_id in self.telemetry_data_dict.keys():

                try:
                    while True:
                        update = self.telemetry_data_dict[subscription_id].get_nowait() 
                        data.append(update)

                except Empty as e:
                        pass


        except Exception as e:

            logger.debug('Exception occured...!')
            logger.debug(e)

        return data


class SubscriptionMessage:

    def __init__(self, xpath, subscription_mode=gnmi_pb2.SAMPLE, sample_interval=2, suppress_redundant=False, heartbeat_interval=5):

        logger.debug(f"xpath:{xpath}")
        path = gnmi_pb2.Path(elem=gNMISession.xpath_to_Path_Element(xpath=xpath))
        logger.debug(f"path:{path}")
        logger.debug(f"mode:{subscription_mode}")
        self.sub = gnmi_pb2.Subscription(path=path,
                                         mode=subscription_mode.value,
                                         sample_interval=sample_interval,
                                         suppress_redundant=suppress_redundant,
                                         heartbeat_interval=heartbeat_interval)

