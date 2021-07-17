from Controller.RdHc import RdHc
import asyncio
from Database.Db import Db
import logging
from logging.handlers import TimedRotatingFileHandler
from HcServices.Http import Http
from HcServices.Signalr import Signalr
from HcServices.Mqtt import Mqtt
from Handler.MqttDataHandler import MqttDataHandler
from Handler.SignalrDataHandler import SignalrDataHandler
import os

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

http = Http()
signalr = Signalr(logger)
mqtt = Mqtt(logger)

signalrHandler = SignalrDataHandler(logger, mqtt, signalr)
mqttHandler = MqttDataHandler(logger, mqtt, signalr)

db = Db()
hc = RdHc(logger, http, signalr, mqtt, mqttHandler, signalrHandler)


async def main():      
    db.init()
    await hc.run()

loop = asyncio.get_event_loop()
loop.create_task(main())
loop.run_forever()
