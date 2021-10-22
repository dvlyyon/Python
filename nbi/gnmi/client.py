import logging
import time
from nbi.gnmi.gnmi_enum import *

logger = logging.getLogger(__name__)

class GrpcClient:

    def __init__(self, ip, port, user=None, passwd=None, cert_path=None,
                 ca_cert=None, client_cert=None, client_key=None,
                 ssl_target_name_override='localhost', secure_connection_type=True):


            from nbi.gnmi.v0_7_0.client070 import gNMISession as gnmi_V7

            self.gRPC_Instance = gnmi_V7(ipAddress=ip,
                                         gnmi_port=port,
                                         username=user,
                                         password=passwd,
                                         certificate_path=cert_path,
                                         ca_cert=ca_cert,
                                         client_cert=client_cert,
                                         client_key=client_key,
                                         ssl_target_name_override=ssl_target_name_override,
                                         secure_connection_type=secure_connection_type)


    def get_capabilities(self):

        return self.gRPC_Instance.capabilities()


    def close_session(self):

        self.gRPC_Instance.close_channel()

    def telemetry_data(self,subscription_id):

        return self.gRPC_Instance.telemetry_data(subscription_id=subscription_id)

    def poll_subscription(self,subscription_id):

        return self.gRPC_Instance.poll_subscription(subscription_id=subscription_id)

    def subscribe(self,subscription_id,subscription_list,mode,encoding,
                    prefix_xpath=None,use_aliases=False,
                    qos=None,allow_aggregation=False,
                    use_models=None,updates_only=False,
                    poll=None,aliases=None, ):


        return self.gRPC_Instance.subscribe(subscription_list=subscription_list,
                                               mode=mode,
                                               prefix_xpath=prefix_xpath,
                                               use_aliases=use_aliases,
                                               qos=qos,
                                               allow_aggregation=allow_aggregation,
                                               use_models=use_models,
                                               updates_only=updates_only,
                                               encoding=encoding,
                                               poll=poll,
                                               aliases=aliases,
                                               subscription_id=subscription_id)


if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)
    client  = GrpcClient(ip='172.29.202.84',port=50051, user='administrator',passwd='e2e!Net4u#',
            cert_path="/home/dyang/Workspace/repos/G30/G30_R5.0/scripts/grpc/G30_Certificates/",
            ssl_target_name_override="infinera.com.cn",
            ca_cert="infr-ca.crt"
            )
    output = client.get_capabilities()
    print(output)
    output = client.subscribe(1,[{GnmiSubscriptionKey.PATH : '/ne/ne-name', 
                              GnmiSubscribeKey.MODE : GnmiStreamMode.SAMPLE}],
                              GnmiSubscribeMode.ONCE,encoding=GnmiSubscribeEncoding.JSON_IETF,
                              )
    time.sleep(10)    
    output = client.telemetry_data(1)
    client.close_session()
    print(output)

