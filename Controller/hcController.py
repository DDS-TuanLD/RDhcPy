from Services.httpServices import HttpAsyncServices
from Services.signalrServices import SignalrServices
from Services.mqttServices import MqttServices
import asyncio
from Database.Db import Db
from Context.DbContext import MySqlDbContext, IContext
import os
import aiohttp
from Cache.HcCache import HcCache
class HcController:
    __httpServices: HttpAsyncServices
    __signalServices: SignalrServices
    __mqttServices: MqttServices
    __db: Db
    __cache : HcCache
    
    def __init__(self, DbContext: IContext):
        self.__httpServices = HttpAsyncServices()
        self.__signalServices = SignalrServices()
        self.__mqttServices = MqttServices()
        self.__Db = Db(DbContext)
        self.__cache = HcCache()
    
    @property
    def HcHttpServices(self):
        return self.__httpServices
    
    @property 
    def HcMqttServices(self):
        return self.__mqttServices
    
    @property
    def HcSignalrServices(self):
        return self.__signalServices
    
    async def __getAndSaveRefreshToken(self):
        refreshTokenHeader = self.HcHttpServices.CreateNewHttpHeader()
        refreshTokenUrl = os.getenv("SERVER_HOST") + os.getenv("REFRESH_TOKEN_URL")
        refreshTokenBody = {
            "username": os.getenv("USERNAME"),
            "password": os.getenv("PASSWORD"),
            "deviceName": os.getenv("DEVICENAME")
            }
        refreshTokenReq = self.HcHttpServices.CreateNewHttpRequest(url= refreshTokenUrl, body_data= refreshTokenBody)
        session = aiohttp.ClientSession()
        res = await self.HcHttpServices.UsePostRequest(session, refreshTokenReq)
        data = await res.json()
        refreshToken = data["RefreshToken"]
        self.__cache.SaveRefreshToken(refreshToken)
    
    async def __getToken(self):
        pass
    
    async def __HcCheckConnectWithCloud(self):
        while True:
            try:
                self.HcSignalrServices.SendMesageToServer(mess="OnConnect")
                await asyncio.sleep(5)
            except Exception as err:
                self.__cache.SignalrConnectStatus = False
            await asyncio.sleep(10)
            if self.__cache.SignalrConnectStatus == False:
                self.__cache.SignalrDisconnectCount = self.__cache.SignalrDisconnectCount + 1
                self.__signalServices.StartConnect()
                print(self.__cache.SignalrDisconnectCount)
                print(self.__cache.SignalrDisconnectStatusUpdate)
                if (self.__cache.SignalrDisconnectCount == 3) and (self.__cache.SignalrDisconnectStatusUpdate == False):
                    self.__cache.SignalrDisconnectStatusUpdate = True
                    self.__cache.SignalrDisconnectCount = 0
                    
    
    async def HcServicesRun(self):
        task = asyncio.ensure_future(self.__mqttServices.MqttServicesInit())
        task1 = asyncio.ensure_future(self.__signalServices.SignalrServicesInit())
        task2 = asyncio.ensure_future(self.__mqttServices.MqttHandlerData())
        task3 = asyncio.ensure_future(self.__signalServices.OnHandlerReceiveData())
        task4 = asyncio.ensure_future(self.__HcCheckConnectWithCloud())
        tasks = [task, task1, task2, task3, task4]
        await asyncio.gather(*tasks)
        return