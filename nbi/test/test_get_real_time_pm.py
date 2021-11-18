import os
import time
import logging
from logging.handlers import RotatingFileHandler
from nbi.gnmi.client import *

logger = logging.getLogger(__name__)

def main():
    client  = GrpcClient(ip='aaa.aaa.aaa.aaa',port=50051, user='administrator',passwd='xxxxxxxx',
            cert_path="/home/dyang/Workspace/repos/G30/G30_R5.0/scripts/grpc/G30_Certificates/",
            ssl_target_name_override="infinera.com.cn",
            ca_cert="infr-ca.crt"
            )
    output = client.subscribe(1,[{GnmiSubscriptionKey.PATH : '/pm/real-time-pm-data/real-time-pm', 
                              GnmiSubscribeKey.MODE : GnmiStreamMode.SAMPLE}],
                              GnmiSubscribeMode.STREAM,encoding=GnmiSubscribeEncoding.JSON_IETF,
                              )
    for i in range(48*60):
        time.sleep(60)    
        output = client.telemetry_data(1)
        logger.critical(f"Notification\n: {output}")
    client.close_session()


if __name__ == "__main__":
    filePath = "get_real_time_pm_48h.log"
    logging.basicConfig(level=logging.ERROR, 
            format='%(asctime)s - %(threadName)s - %(levelname)s -  %(message)s',
            datefmt='%m-%d %H:%M')
    rfh = RotatingFileHandler(filePath, maxBytes=100*1024*1024, backupCount=10, mode='w')
    rfh.setLevel(logging.CRITICAL)
    fmt = logging.Formatter('%(asctime)s - %(threadName)s - %(levelname)s -  %(message)s',
            datefmt='%m-%d %H:%M')
    rfh.setFormatter(fmt)
    main()
