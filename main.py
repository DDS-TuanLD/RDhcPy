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

loghandler = logging.handlers.TimedRotatingFileHandler(filename= d + '/Logging/runtime.log', when="MIDNIGHT", backupCount=4)
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

async def main():      
    db.Init()
    await hc.Run()

loop = asyncio.get_event_loop()
loop.create_task(main())
loop.run_forever()