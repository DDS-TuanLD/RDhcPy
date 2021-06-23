from Controller.hcController import HcController
import asyncio
import requests
from Database.Db import Db
import datetime
import threading        
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import Constant.constant as const 
from HcServices.mqttServices import MqttServices, MqttConfig
from HcServices.httpServices import HttpServices
from HcServices.signalrServices import SignalrServices
import socket

d = os.path.dirname(__file__)

loghandler = logging.handlers.TimedRotatingFileHandler(filename= d + '/Logging/runtime.log', when="D", backupCount=4)
logfomatter = logging.Formatter(fmt=(
                                                    '%(asctime)s:\t'
                                                    '%(levelname)s:\t'
                                                    '%(filename)s:'
                                                    '%(funcName)s():'
                                                    '%(lineno)d\t'
                                                    '%(message)s'
                                                ))
logger = logging.getLogger("mylog")
loghandler.setFormatter(logfomatter)
logger.addHandler(loghandler)
logger.setLevel(logging.DEBUG)

hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)

mqttConfig = MqttConfig(
    host = ip,
    port = const.MQTT_PORT,
    qos = const.MQTT_QOS,
    keepalive = const.MQTT_KEEPALIVE,
    username = const.MQTT_USER,
    password = const.MQTT_PASS
)

mqttService = MqttServices(logger, mqttConfig) 
httpService = HttpServices(logger)
signalrService = SignalrServices(logger)
db = Db()

hc = HcController(logger, httpService=httpService, mqttService=mqttService, signalrService=signalrService, db=db)

def hc_db_thread(db: Db, hc: HcController):
    db.Init(const.DB_NAME)
    asyncio.run(hc.ActionDb())
    
def hc_no_db_thread(hc: HcController):
    asyncio.run(hc.ActionNoDb())
    
def hc_mqtt_init_thread(hc: HcController):
    asyncio.run(hc.MqttInit())
    
def main():  
    threads = []
    threads.append(threading.Thread(target = hc_db_thread, args=(db, hc,)))
    threads.append(threading.Thread(target = hc_no_db_thread, args=(hc,)))
    threads.append(threading.Thread(target = hc_mqtt_init_thread, args=(hc,)))
    
    [thread.start() for thread in threads]
    [thread.join() for thread in threads]


if __name__ == "__main__":
    main()