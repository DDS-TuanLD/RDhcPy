from Controller.Hc import RdHc
import asyncio
import requests
from Database.Db import Db
import datetime
import threading        
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import Constant.constant as const 
import socket
from Contracts.IController import IController
from sqlalchemy.sql.expression import BinaryExpression


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

db= Db()
hc= RdHc(logger)

def hc_db_thread(db: Db, hc: IController):
    db.Init()
    asyncio.run(hc.ActionDb())
    
def hc_no_db_thread(hc: IController):
    asyncio.run(hc.ActionNoDb())

def main():      
    threads = []
    threads.append(threading.Thread(target = hc_db_thread, args=(db, hc,)))
    threads.append(threading.Thread(target = hc_no_db_thread, args=(hc,)))
    
    [thread.start() for thread in threads]
    [thread.join() for thread in threads]


if __name__ == "__main__":
    main()