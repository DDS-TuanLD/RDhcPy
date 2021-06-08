from BaseServices.httpServices import HttpServices
from BaseServices.signalrServices import SignalrServices
from BaseServices.mqttServices import MqttServices
import asyncio
from Database.Db import Db
from Context.DbContext import MySqlDbContext, IContext
class HcController:
    __httpServices: HttpServices
    __signalServices: SignalrServices
    __mqttServices: MqttServices
    __db: Db
    
    def __init__(self, DbContext: IContext):
        self.__httpServices = HttpServices()
        self.__signalServices = SignalrServices()
        self.__mqttServices = MqttServices()
        self.__Db = Db(DbContext)
    
    def HcServicesStart(self):
        self.__mqttServices.MqttConnect()
        self.__mqttServices.MqttStartLoop()

        self.__signalServices.ConnectToServer()
        self.__signalServices.StartServices()
        self.__signalServices.OnReceiveData()
    
    async def HcServicesRun(self):
        task2 = asyncio.ensure_future(self.__mqttServices.MqttHandlerData())
        task3 = asyncio.ensure_future(self.__signalServices.OnHandlerReceiveData())
        tasks = [task2, task3]
        await asyncio.gather(*tasks)
        return