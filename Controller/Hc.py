from HcServices.Http import Http
from HcServices.Signalr import Signalr
from HcServices.Mqtt import Mqtt
import asyncio
from Database.Db import Db
import aiohttp
from Cache.Cache import Cache
import Constant.constant as const
import datetime
from Model.systemConfiguration import systemConfiguration
import time
from Model.userData import userData
import logging
import threading
import http
import json
from Contracts.Itransport import Itransport
from Contracts.IController import IController
from Helper.System import System
from Contracts.Ihandler import Ihandler
from Handler.MqttDataHandler import MqttDataHandler
from Handler.SignalrDataHandler import SignalrDataHandler

class RdHc(IController):
    __httpServices: Http
    __signalServices: Itransport
    __mqttServices: Itransport
    __db: Db
    __cache : Cache
    __lock: threading.Lock
    __logger: logging.Logger
    __mqttHandler: Ihandler
    __signalrHandler: Ihandler
    
    def __init__(self, log: logging.Logger):
        self.__logger = log
        self.__httpServices = Http()
        self.__signalServices = Signalr(self.__logger)
        self.__mqttServices = Mqtt(self.__logger)
        self.__db = Db()
        self.__cache = Cache()
        self.__lock = threading.Lock()
        self.__mqttHandler =  MqttDataHandler(self.__logger, self.__mqttServices, self.__signalServices)
        self.__signalrHandler =  SignalrDataHandler(self.__logger, self.__mqttServices, self.__signalServices)
        
    #-----------------Ping cloud----------------------------------------------------------------------
    async def __HcCheckConnectWithCloud(self):
        s = System(self.__logger)
        while True:  
            print("Hc send heardbeat to cloud")
            self.__logger.info("Hc send heardbeat to cloud")
            if self.__cache.DisconnectTime == None:
                self.__cache.DisconnectTime = datetime.datetime.now()
            ok = await s.SendHttpRequestToHeardbeatUrl(self.__httpServices)
            if ok == False:
                print("can not ping to cloud")
                self.__cache.SignalrDisconnectCount = self.__cache.SignalrDisconnectCount + 1 
                self.__cache.SignalrConnectSuccessFlag = False 
                self.__cache.PingCloudSuccessFlag = False
            if ok == True:
                await s.RecheckReconnectStatusOfLastActiveInDb()
                if self.__cache.FirstPingSuccessToCloudFlag == False:
                    self.__cache.FirstPingSuccessToCloudFlag = True
                self.__cache.PingCloudSuccessFlag = True
                self.__cache.DisconnectTime = None
                self.__cache.SignalrDisconnectCount = 0
            # if (ok == True) and (self.__cache.SignalrDisconnectStatusUpdateStatusFlag == True):
            #     self.__cache.SignalrDisconnectStatusUpdateStatusFlag = False
            #     await self.__hcUpdateReconnectStToDb()     
            await asyncio.sleep(15)
            if (self.__cache.SignalrDisconnectCount == 3) and (self.__cache.SignalrDisconnectStatusUpdateStatusFlag == False):
                # self.__cache.SignalrDisconnectStatusUpdateStatusFlag = True
                # self.__cache.SignalrDisconnectCount = 0  
                self.__hcUpdateDisconnectStToDb()
                if self.__cache.FirstPingSuccessToCloudFlag == True:
                    s.EliminateCurrentProgess()
     
    async def __hcUpdateReconnectStToDb(self):
        self.__logger.info("Update cloud reconnect status to db")
        print("Update cloud reconnect status to db")
        s = System(self.__logger)
        await s.UpdateReconnectStatusToDb(reconnectTime=datetime.datetime.now())
        
    def __hcUpdateDisconnectStToDb(self):
        self.__logger.info("Update cloud disconnect status to db")
        print("Update cloud disconnect status to db")
        s = System(self.__logger)
        s.UpdateDisconnectStatusToDb(DisconnectTime=self.__cache.DisconnectTime) 
    #--------------------------------------------------------------------------------------
    
    #------------------Mqtt data handler---------------------------------------------------         
    async def __HcHandlerMqttData(self):
        """ This function handler data received in queue
        """
        while True:
            await asyncio.sleep(0.1)
            if self.__mqttServices.mqttDataQueue.empty() == False:
                with self.__lock:
                    item = self.__mqttServices.mqttDataQueue.get()
                    self.__mqttHandler.Handler(item)
                    self.__mqttServices.mqttDataQueue.task_done()

    #------------------- Signalr data handler--------------------------------------------------------
    async def __HcHandlerSignalRData(self):
        while True:
            await asyncio.sleep(0.1)
            if self.__signalServices.signalrDataQueue.empty() == False:
                with self.__lock:
                    item = self.__signalServices.signalrDataQueue.get()
                    self.__signalrHandler.Handler(item)
                    self.__signalServices.signalrDataQueue.task_done()
                     
    #-----------load userdata from db----------------------------------------------------------
    def __HcLoadUserData(self):
        userData = self.__db.Services.UserdataServices.FindUserDataById(id=1)
        dt = userData.first()
        if dt != None:
            self.__cache.EndUserId = dt["EndUserProfileId"]
            self.__cache.RefreshToken = dt["RefreshToken"]   
    #------------------------------------------------------------------------------------------
    
    #-------------main function----------------------------------------------------------------
    async def ActionNoDb(self):
        task1 = asyncio.ensure_future(self.__signalServices.Init())
        task2 = asyncio.ensure_future(self.__mqttServices.Init())
        tasks = [task1, task2]
        await asyncio.gather(*tasks)
        return

    async def ActionDb(self): 
        self.__HcLoadUserData()
        task1 = asyncio.ensure_future(self.__HcHandlerSignalRData())
        task2 = asyncio.ensure_future(self.__HcCheckConnectWithCloud())
        task3 = asyncio.ensure_future(self.__HcHandlerMqttData())     
        tasks = [task1, task2, task3]
        await asyncio.gather(*tasks)
        return
    