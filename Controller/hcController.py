from Services.httpServices import HttpAsyncServices
from Services.signalrServices import SignalrServices
from Services.mqttServices import MqttServices
import asyncio
from Database.Db import Db
import os
import aiohttp
from Cache.HcCache import HcCache
from Model.systemConfiguration import systemConfiguration
import datetime
class HcController:
    __httpServices: HttpAsyncServices
    __signalServices: SignalrServices
    __mqttServices: MqttServices
    __db: Db
    __cache : HcCache
    
    def __init__(self):
        self.__httpServices = HttpAsyncServices()
        self.__signalServices = SignalrServices()
        self.__mqttServices = MqttServices()
        self.__Db = Db()
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
            "username": os.getenv("USER"),
            "password": os.getenv("PASS"),
            "deviceName": os.getenv("DEVICENAME")
            }
        refreshTokenReq = self.HcHttpServices.CreateNewHttpRequest(url= refreshTokenUrl, body_data=refreshTokenBody)
        session = aiohttp.ClientSession()
        res = await self.HcHttpServices.UsePostRequest(session, refreshTokenReq)
        try:
            data = await res.json()
            self.__cache.RefreshToken = data['refreshToken']
            self.__cache.EndUserId = str(data['endUserProfiles'][0]['id'])
        except Exception as err:
            print(f"Error when get refresh token")
        await session.close()
        return
    
    async def __getToken(self):
        refreshToken = self.__cache.RefreshToken
        tokenUrl = os.getenv("SERVER_HOST") + os.getenv("TOKEN_URL")
        cookie = f"RefreshToken={refreshToken}"
        header = self.HcHttpServices.CreateNewHttpHeader(cookie = cookie)
        req = self.HcHttpServices.CreateNewHttpRequest(url=tokenUrl, header=header)
        session = aiohttp.ClientSession()
        token = ""
        try:
            res = await self.HcHttpServices.UsePostRequest(session, req)
            data = await res.json()
            token = data['token']
        except Exception as err:
            print("Error when get token")
        await session.close()
        return token
    
    async def __HcCheckConnectWithCloud(self):
        while True:
            endUser = self.__cache.EndUserId
            try:
                print("Hc send heardbeat to cloud")
                self.HcSignalrServices.SendMesageToServer(endUserProfileId=endUser,entity= "Heardbeat", message= "ping")
                await asyncio.sleep(5)
            except Exception as err:
                print(f"Exception when send heardbeat {err}")
            await asyncio.sleep(5)
            if self.__cache.DisconnectTime == None:
                self.__cache.DisconnectTime = datetime.datetime.now()
            self.__cache.SignalrDisconnectCount = self.__cache.SignalrDisconnectCount + 1
            self.__signalServices.StartConnect()
            if (self.__cache.SignalrDisconnectCount == 3) and (self.__cache.SignalrDisconnectStatusUpdate == False):
                
                print("Update cloud disconnect status to db")
                await self.__Db.DbSystemConfigurationRepo.CreateWithParamsAsync(IsConnect=True, DisconnectTime=self.__cache.DisconnectTime, ReconnectTime=None)
                self.__cache.SignalrDisconnectStatusUpdate = True
                self.__cache.SignalrDisconnectCount = 0   
    
    async def HcServicesRun(self):
        await self.__getAndSaveRefreshToken()
        task1 = asyncio.ensure_future(self.__mqttServices.MqttServicesInit())
        task2 = asyncio.ensure_future(self.__signalServices.SignalrServicesInit())
        task3 = asyncio.ensure_future(self.__mqttServices.MqttHandlerData())
        task4 = asyncio.ensure_future(self.__signalServices.OnHandlerReceiveData())
        task5 = asyncio.ensure_future(self.__HcCheckConnectWithCloud())
        tasks = [task1, task2, task3, task4, task5]
        await asyncio.gather(*tasks)
        return