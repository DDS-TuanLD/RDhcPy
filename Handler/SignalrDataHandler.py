from HcServices.Mqtt import Mqtt
from HcServices.Signalr import Signalr
from Contracts.Itransport import Itransport
from Contracts.Ihandler import Ihandler
import asyncio
import logging
from Cache.GlobalVariables import GlobalVariables
from Database.Db import Db
import Constant.constant as const


class SignalrDataHandler(Ihandler):
    __logger: logging.Logger
    __mqtt: Itransport
    __signalr: Itransport
    __db: Db
    __globalVariables: GlobalVariables

    def __init__(self, log: logging.Logger, mqtt: Itransport, signalr: Itransport):
        self.__logger = log
        self.__mqtt = mqtt
        self.__db = Db()
        self.__globalVariables = GlobalVariables()
        self.__signalr = signalr
        
    def Handler(self, args):
        entity = args[0]
        data = args[1]
        self.__logger.debug(f"handler receive signal data in {entity} is {data}")
        print(f"handler receive signal data in {entity} is {data}")
        try:
            switcher = {
                const.SIGNALR_APP_COMMAND_ENTITY: self.__handlerEntityCommand
            }
            func = switcher.get(entity)
            func(data)
        except:
            self.__logger.error("data receive from signal invalid")
            print("data receive from signal invalid")
        return

    def __handlerEntityCommand(self, data):
        self.__mqtt.Send(const.MQTT_CONTROL_TOPIC, data, const.MQTT_QOS)