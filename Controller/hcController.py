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
import threading
import http
class HcController():
    __httpServices: HttpAsyncServices
    __signalServices: SignalrServices
    __mqttServices: MqttServices
    __db: Db
    __cache : HcCache
    __logger: logging.Logger
    __lock: threading.Lock
    
    def __init__(self, log: logging.Logger):   
        self.__logger = log
        self.__httpServices = HttpAsyncServices(self.__logger)
        self.__signalServices = SignalrServices(self.__logger)
        self.__mqttServices = MqttServices(self.__logger)
        self.__db = Db()
        self.__cache = HcCache()
        self.__lock = threading.Lock()
        
    @property
    def HcHttpServices(self):
        return self.__httpServices
    
    @property 
    def HcMqttServices(self):
        return self.__mqttServices
    
    @property
    def HcSignalrServices(self):
        return self.__signalServices
     
    async def __hcGetToken(self):
        refreshToken = self.__cache.RefreshToken
        if refreshToken == "":
            return ""
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
            
    async def __hcSendHttpRequestToHeardbeatUrl(self):
        endUser = self.__cache.EndUserId
        try:
            token = await self.__hcGetToken() 
        except:
            token = ""
        cookie = f"Token={token}"
        heardBeatUrl = const.SERVER_HOST + const.SIGNSLR_HEARDBEAT_URL
        header = self.HcHttpServices.CreateNewHttpHeader(cookie = cookie, endProfileId=self.__cache.EndUserId)
        req = self.HcHttpServices.CreateNewHttpRequest(url=heardBeatUrl, header=header)
        session = aiohttp.ClientSession()
        res = await self.HcHttpServices.UsePostRequest(session, req)
        await session.close()
        if res == "":
            return False
        if (res != "") and (res.status == http.HTTPStatus.OK):
            return True
    
    async def __hcCheckConnectWithCloud(self):
        while True:  
            self.__logger.info("Hc send heardbeat to cloud")
            print("Hc send heardbeat to cloud")
            if self.__cache.DisconnectTime == None:
                self.__cache.DisconnectTime = datetime.datetime.now()
            ok = await self.__hcSendHttpRequestToHeardbeatUrl()
            if ok == False:
                self.__cache.SignalrDisconnectCount = self.__cache.SignalrDisconnectCount + 1    
            if ok == True:
                self.__cache.DisconnectTime = None
            if (ok == True) and (self.__cache.SignalrDisconnectStatusUpdate == True):
                await self.__signalServices.StartConnect()
                self.__logger.info("Update cloud reconnect status to db")
                print("Update cloud reconnect status to db")
                self.__cache.SignalrDisconnectCount = 0
                s =systemConfiguration(isConnect= True, DisconnectTime= None, ReconnectTime= datetime.datetime.now())
                self.__db.DbServices.SystemConfigurationServices.AddNewSysConfiguration(s)
                self.__cache.SignalrDisconnectStatusUpdate = False  
            await asyncio.sleep(10)
            if (self.__cache.SignalrDisconnectCount == 3) and (self.__cache.SignalrDisconnectStatusUpdate == False):
                self.__logger.info("Update cloud disconnect status to db")
                s =systemConfiguration(isConnect= False, DisconnectTime= self.__cache.DisconnectTime, ReconnectTime= None)
                self.__db.DbServices.SystemConfigurationServices.AddNewSysConfiguration(s)
                self.__cache.SignalrDisconnectStatusUpdate = True
                self.__cache.SignalrDisconnectCount = 0    
            if self.__cache.SignalrDisconnectStatusUpdate > 3:
                self.__cache.SignalrDisconnectCount = 0
    
    async def HcCheckMqttConnect(self):
        while True:
            try:
                self.HcMqttServices.MqttPublish("ping", qos=0)
                await asyncio.sleep(15)
            except Exception as err:
                self.__logger.error("Error when ping to mqtt")
                print("Error when ping to mqtt")
                self.__mqttServices.MqttDisconnect()
                await self.__mqttServices.MqttServicesInit()
                await asyncio.sleep(15)
                
    async def __hcMqttHandlerData(self):
        """ This function handler data received in queue
        """
        while True:
            await asyncio.sleep(0.1)
            if self.__mqttServices.mqttDataQueue.empty() == False:
                with self.__lock:
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
            await asyncio.sleep(0.1)
            if self.__signalServices.signalrDataQueue.empty() == False:
                with self.__lock:
                    item = self.__signalServices.signalrDataQueue.get()
                    self.__signalrItemHandler(item)
        
    def __signalrItemHandler(self, *args):
        print(args[0][1])
        # switcher = {
           
        # }
        # func = switcher.get(args[0][0])
        # func(args[0][1])
        pass

    
    async def HcActionNoDb(self):
        task1 = asyncio.ensure_future(self.__signalServices.SignalrServicesInit())
        task2 = asyncio.ensure_future(self.__hcMqttHandlerData())
        tasks = [task1, task2]
        await asyncio.gather(*tasks)
        return

    async def HcActionDb(self):
        task1 = asyncio.ensure_future(self.__hcHandlerSignalRData())
        task2 = asyncio.ensure_future(self.__hcCheckConnectWithCloud())
        tasks = [task1, task2]
        await asyncio.gather(*tasks)
        return
    