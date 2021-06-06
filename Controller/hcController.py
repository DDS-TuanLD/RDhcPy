from BaseServices.httpServices import HttpServices
from BaseServices.signalrServices import SignalrServices
from BaseServices.mqttServices import MqttServices
import asyncio

class HcController:
    __httpServices: HttpServices
    __signalServices: SignalrServices
    __mqttServices: MqttServices
    
    def __init__(self):
        self.__httpServices = HttpServices()
        self.__signalServices = SignalrServices()
        self.__mqttServices = MqttServices()
    
    async def RunForever(self):
        self.__mqttServices.MqttConnect()
        self.__mqttServices.MqttStartLoop()

        self.__signalServices.ConnectToServer()
        self.__signalServices.Start()
        self.__signalServices.OnReceiveData()

        task2 = asyncio.ensure_future(self.__mqttServices.MqttHandlerData())
        task3 = asyncio.ensure_future(self.__signalServices.OnHandlerReceiveData())
        tasks = [task2, task3]
        await asyncio.gather(*tasks)
        return