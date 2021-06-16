from HcServices.httpServices import HttpAsyncServices
from HcServices.signalrServices import SignalrServices
from HcServices.mqttServices import MqttServices
import asyncio
from Database.Db import Db
import aiohttp
from Cache.HcCache import HcCache
from Model.systemConfiguration import systemConfiguration
import Constant.constant as const
import datetime
from Model.systemConfiguration import systemConfiguration
import time
from Adapter.dataAdapter import dataAdapter
import logging
class HcController():
    __httpServices: HttpAsyncServices
    __signalServices: SignalrServices
    __mqttServices: MqttServices
    __db: Db
    __cache : HcCache
    __logger: logging.Logger
    
    def __init__(self, log: logging.Logger):   
        self.__logger = log
        self.__httpServices = HttpAsyncServices(self.__logger)
        self.__signalServices = SignalrServices(self.__logger)
        self.__mqttServices = MqttServices(self.__logger)
        self.__db = Db()
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
        refreshTokenUrl = const.SERVER_HOST + const.REFRESH_TOKEN_URL
        refreshTokenBody = {
            "username": const.USER,
            "password": const.PASS,
            "deviceName": const.DEVICENAME
            }
        refreshTokenReq = self.HcHttpServices.CreateNewHttpRequest(url= refreshTokenUrl, body_data=refreshTokenBody)
        session = aiohttp.ClientSession()
        res = await self.HcHttpServices.UsePostRequest(session, refreshTokenReq)
        if res != "":
            data = await res.json()
            refreshToken = data['refreshToken']
            endUserId = str(data['endUserProfiles'][0]['id'])
            self.__logger.debug("Get RefreshToken and endUserId successful")
            if refreshToken != None:
                self.__cache.RefreshToken = data['refreshToken']
            if endUserId != None:
                self.__cache.EndUserId = endUserId
        await session.close()
        return
    
    async def __getToken(self):
        refreshToken = self.__cache.RefreshToken
        tokenUrl = const.SERVER_HOST + const.TOKEN_URL
        cookie = f"RefreshToken={refreshToken}"
        header = self.HcHttpServices.CreateNewHttpHeader(cookie = cookie, endProfileId=self.__cache.EndUserId)
        req = self.HcHttpServices.CreateNewHttpRequest(url=tokenUrl, header=header)
        session = aiohttp.ClientSession()
        res = await self.HcHttpServices.UsePostRequest(session, req)
        if res != "":
            data = await res.json()
            token = data['token']
        await session.close()
        return token
    
    async def __hcUpdateRefreshToken(self):
        while True:
            await self.__getAndSaveRefreshToken()
            self.__logger.info("Update refresh Token")
            print("Update refresh Token")
            await asyncio.sleep(30)
    
    async def __hcCheckConnectWithCloud(self):
        while True:
            endUser = self.__cache.EndUserId
            self.__logger.info("Hc send heardbeat to cloud")
            print("Hc send heardbeat to cloud")
            self.HcSignalrServices.SendMesageToServer(endUserProfileId=endUser,entity= "Heardbeat", message= "ping")          
            if self.__cache.DisconnectTime == None:
                self.__cache.DisconnectTime = datetime.datetime.now()
            await asyncio.sleep(10)
            self.__cache.SignalrDisconnectCount = self.__cache.SignalrDisconnectCount + 1
            self.__signalServices.StartConnect()
            if (self.__cache.SignalrDisconnectCount == 3) and (self.__cache.SignalrDisconnectStatusUpdate == False):
                self.__logger.info("Update cloud disconnect status to db")
                s =systemConfiguration(isConnect= False, DisconnectTime= self.__cache.DisconnectTime, ReconnectTime= None)
                self.__db.DbServices.SystemConfigurationServices.AddNewSysConfiguration(s)
                self.__cache.SignalrDisconnectStatusUpdate = True
                self.__cache.SignalrDisconnectCount = 0   
            if self.__cache.SignalrDisconnectCount == 3:
                self.__cache.SignalrDisconnectCount = 0   

    
    async def HcCheckMqttConnect(self):
        while True:
            try:
                self.HcMqttServices.MqttPublish("ping", qos=2)
                await asyncio.sleep(15)
            except Exception as err:
                print("Error when ping to mqtt")
                self.__mqttServices.MqttStopLoop()
                self.__mqttServices.MqttDisconnect()
                await self.__mqttServices.MqttServicesInit()
                await asyncio.sleep(15)
                
    
            # self.__cache.mqttDisconnectStatus = True
            # if (self.__cache.mqttDisconnectStatus == True):
            #     self.__logger.info("Reconnect to mqtt")
            #     self.__cache.mqttProblemCount = 0

    async def __hcMqttHandlerData(self):
        """ This function handler data received in queue
        """
        while True:
            await asyncio.sleep(0.5)
            if self.__mqttServices.mqttDataQueue.empty() == False:
                item = self.__mqttServices.mqttDataQueue.get()
                self.__mqttItemHandler(item)

    def __mqttItemHandler(self, args):
        print(args)
        dtAdapter = dataAdapter()
        if args == "ping":
            self.__logger.debug("Hc is connecting with mqtt broker")
            self.__cache.mqttDisconnectStatus = False
            self.__cache.mqttProblemCount = 0
            return
        newdata = dtAdapter.hcToCloudAdapter(args)

        
    async def __hcHandlerSignalRData(self):
        while True:
            await asyncio.sleep(0.5)
            if self.__signalServices.signalrDataQueue.empty() == False:
                item = self.__signalServices.signalrDataQueue.get()
                self.__signalrItemHandler(item)
        
    def __signalrItemHandler(self, *args):
        switcher = {
            "Heardbeat": self.__heardbeatHandler,
            "LedControlTesting": self.__ledControlTestingHandler
        }
        func = switcher.get(args[0][0])
        func(args[0][1])
    
    def __heardbeatHandler(self, data: str=""):
        if data == "pong":
            self.__cache.SignalrDisconnectCount = 0
            if self.__cache.SignalrDisconnectStatusUpdate == True:
                self.__logger.info("Update cloud reconnect status to db")
                s =systemConfiguration(isConnect= True, DisconnectTime= None, ReconnectTime= datetime.datetime.now())
                self.__db.DbServices.SystemConfigurationServices.AddNewSysConfiguration(s)
                self.__cache.SignalrDisconnectStatusUpdate = False
                self.__cache.DisconnectTime = None
            
    def __ledControlTestingHandler(self, data: str=""):
        dataAdapter = dataAdapter()
        newdata = dataAdapter.cloudToHcAdapter()
        pass
    
    async def HcActionNoDb(self):
        task1 = asyncio.ensure_future(self.__signalServices.SignalrServicesInit())
        task2 = asyncio.ensure_future(self.__hcMqttHandlerData())
        task3 = asyncio.ensure_future(self.__hcUpdateRefreshToken())
        tasks = [task1, task2, task3]
        await asyncio.gather(*tasks)
        return

    async def HcActionDb(self):
        task1 = asyncio.ensure_future(self.__hcHandlerSignalRData())
        task2 = asyncio.ensure_future(self.__hcCheckConnectWithCloud())
        tasks = [task1, task2]
        await asyncio.gather(*tasks)
        return
    