from HcServices.Mqtt import Mqtt
from HcServices.Signalr import Signalr
from Contracts.Itransport import Itransport
from Contracts.Ihandler import Ihandler
import asyncio
import logging
from Cache.Cache import Cache
from Database.Db import Db
import Constant.constant as const

class SignalrDataHandler(Ihandler):
    __logger: logging.Logger
    __mqtt: Itransport
    __signalr: Itransport
    __db: Db
    __cache: Cache

    def __init__(self, log: logging.Logger, mqtt: Itransport, signalr: Itransport):
        self.__logger = log
        self.__mqtt = mqtt
        self.__db = Db()
        self.__cache = Cache()
        self.__signalr = signalr
        
    def Handler(self, *args):
        self.__logger.debug(f"handler receive signal data in {args[0][0]} is {args[0][1]}")
        print(f"handler receive signal data in {args[0][0]} is {args[0][1]}")
        try:
            switcher = {
                const.SIGNALR_APP_COMMAND_ENTITY: self.__handlerEntityCommand
            }
            func = switcher.get(args[0][0])
            func(args[0][1])
        except:
            self.__logger.error("data receive from signal invalid")
            print("data receive from signal invalid")
        return

    def __handlerEntityCommand(self, data):
        self.__mqtt.Send(const.MQTT_CONTROL_TOPIC, data, const.MQTT_QOS)