from Controller.hcController import HcController
import asyncio
import requests
from Database.Db import Db
import datetime
from Model.systemConfiguration import systemConfiguration
from Model.userData import userData
import threading        
import logging
from logging.handlers import TimedRotatingFileHandler
import os

d = os.path.dirname(__file__)
print(d)

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

db = Db()
hc = HcController(logger)

def db_thread(db: Db, hc: HcController):
    db.DbCreateTable()
    db.DbServicesInit() 
    asyncio.run(hc.HcActionDb())
    
def no_db_thread(hc: HcController):
    asyncio.run(hc.HcActionNoDb())

def mqtt_check_connection(hc: HcController):
    asyncio.run(hc.HcCheckMqttConnect())
    
def main():  
    threads = []
    threads.append(threading.Thread(target = db_thread, args=(db, hc,)))
    threads.append(threading.Thread(target = no_db_thread, args=(hc,)))
    threads.append(threading.Thread(target = mqtt_check_connection, args=(hc, )))
    
    [thread.start() for thread in threads]
    [thread.join() for thread in threads]


if __name__ == "__main__":
    main()