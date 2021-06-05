from BaseServices.httpServices import HttpServices
from BaseServices.signalrServices import SignalrClient
from ExtraServices.hcRequestServices import HcRequestServices
from BaseServices.mqttServices import MqttServices
import asyncio

class HcController:

    def __init__(self):
        self.httpServices = HttpServices()
        self.signalServices = SignalrClient()
        self.hcRequestServices = HcRequestServices()
        self.mqttServices = MqttServices()
    
    async def __other_coroutine(self):
        while True:
            await asyncio.sleep(1)
            print("other route")

        
    async def RunForever(self):
        self = HcController()
        self.mqttServices.MqttConnect()
        self.mqttServices.MqttStartLoop()

        self.signalServices.ConnectToServer()
        self.signalServices.Start()
        self.signalServices.OnReceiveData()

        task1 = asyncio.ensure_future(self.__other_coroutine())
        task2 = asyncio.ensure_future(self.mqttServices.MqttHandlerData())
        task3 = asyncio.ensure_future(self.signalServices.OnHandlerReceiveData())
        tasks = [task1, task2, task3]

        await asyncio.gather(*tasks)