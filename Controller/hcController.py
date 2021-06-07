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
    
    async def __on_OtherCoroutine(self):
        while True:
            await asyncio.sleep(1)
            print("This is other coroutine")
    
    async def RunForever(self):
        self.__mqttServices.MqttConnect()
        self.__mqttServices.MqttStartLoop()

        self.__signalServices.ConnectToServer()
        self.__signalServices.StartServices()
        self.__signalServices.OnReceiveData()

        task1 = asyncio.ensure_future(self.__on_OtherCoroutine())
        task2 = asyncio.ensure_future(self.__mqttServices.MqttHandlerData())
        task3 = asyncio.ensure_future(self.__signalServices.OnHandlerReceiveData())
        tasks = [task1, task2, task3]
        await asyncio.gather(*tasks)
        return