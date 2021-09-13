from Contracts.ITransport import ITransport
from Contracts.IHandler import IHandler
import logging
from Cache.GlobalVariables import GlobalVariables
import Constant.constant as const


class SignalrDataHandler(IHandler):
    __logger: logging.Logger
    __mqtt: ITransport
    __signalr: ITransport
    __globalVariables: GlobalVariables

    def __init__(self, log: logging.Logger, mqtt: ITransport, signalr: ITransport):
        self.__logger = log
        self.__mqtt = mqtt
        self.__globalVariables = GlobalVariables()
        self.__signalr = signalr

    def handler(self, item):
        if self.__globalVariables.AllowChangeCloudAccountFlag:
            return
        
        dorId = item[0]
        entity = item[1]
        data = item[2]
        
        if dorId != self.__globalVariables.DormitoryId:
            return
        
        self.__logger.debug(f"handler receive signal data in {entity} is {data}")
        print(f"handler receive signal data in {entity} is {data}")
        try:
            switcher = {
                const.SIGNALR_APP_COMMAND_ENTITY: self.__handler_entity_command
            }
            func = switcher.get(entity)
            func(data)
        except:
            self.__logger.error("data receive from signal invalid")
            print("data receive from signal invalid")
        return

    def __handler_entity_command(self, data):
        self.__mqtt.send(const.MQTT_CONTROL_TOPIC, data)
