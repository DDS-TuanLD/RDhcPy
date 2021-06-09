from BaseServices.httpServices import HttpAsyncServices
from BaseServices.signalrServices import SignalrServices
from BaseServices.mqttServices import MqttServices
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
    
    async def __HcSignalrServicesInit(self):
        self.__signalServices.ConnectToServer()
        startSuccess = False
        while startSuccess == False:
            await asyncio.sleep(2)
            startSuccess = self.__signalServices.StartServices()
        self.__signalServices.OnReceiveData()

    async def __HcMqttServicesInit(self):
        startSuccess = False
        while startSuccess == False:
            await asyncio.sleep(2)
            startSuccess = self.__mqttServices.MqttConnect()
        self.__mqttServices.MqttStartLoop()

    async def __HcCheckConnectWithCloud(self):
        count = 0
        while True:
            await asyncio.sleep(60)
        pass
    
    async def HcServicesRun(self):
        task0 = asyncio.ensure_future(self.__HcMqttServicesInit())
        task1 = asyncio.ensure_future(self.__HcSignalrServicesInit())
        task2 = asyncio.ensure_future(self.__mqttServices.MqttHandlerData())
        task3 = asyncio.ensure_future(self.__signalServices.OnHandlerReceiveData())
         
        tasks = [task2, task3, task1]
        await asyncio.gather(*tasks)
        return