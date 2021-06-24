from HcServices.httpServices import HttpServices
from HcServices.signalrServices import SignalrServices
from HcServices.mqttServices import MqttServices, MqttConfig
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
import json

class HcController():
    __httpServices: HttpServices
    __signalServices: SignalrServices
    __mqttServices: MqttServices
    __db: Db
    __cache : HcCache
    __logger: logging.Logger
    __lock: threading.Lock
    
    def __init__(self, log: logging.Logger, httpService: HttpServices, mqttService: MqttServices, signalrService: SignalrServices, db: Db):   
        self.__logger = log
        self.__httpServices = httpService
        self.__signalServices = signalrService
        self.__mqttServices = mqttService
        self.__db = db
        self.__cache = HcCache()
        self.__lock = threading.Lock()
           
    async def __HcUpdateUserdata(self):
       pass
            
    #-----------------Ping cloud
    async def __HcCheckConnectWithCloud(self):
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
                await self.__signalServices.StartConnect()
            if (ok == True) and (self.__cache.SignalrDisconnectStatusUpdate == True):
                self.__hcUpdateReconnectStToDb()
            await asyncio.sleep(20)
            if (self.__cache.SignalrDisconnectCount == 3) and (self.__cache.SignalrDisconnectStatusUpdate == False):
                self.__hcUpdateDisconnectStToDb()
            if self.__cache.SignalrDisconnectStatusUpdate > 3:
                self.__cache.SignalrDisconnectCount = 0
                
    async def __hcSendHttpRequestToHeardbeatUrl(self):
        endUser = self.__cache.EndUserId
        try:
            token = await self.__hcGetToken() 
        except:
            token = ""
        cookie = f"Token={token}"
        heardBeatUrl = const.SERVER_HOST + const.SIGNSLR_HEARDBEAT_URL
        header = self.__httpServices.CreateNewHttpHeader(cookie = cookie, endProfileId=self.__cache.EndUserId)
        req = self.__httpServices.CreateNewHttpRequest(url=heardBeatUrl, header=header)
        session = aiohttp.ClientSession()
        res = await self.__httpServices.UsePostRequest(session, req)
        await session.close()
        if res == "":
            return False
        if (res != "") and (res.status == http.HTTPStatus.OK):
            return True
        
    async def __hcGetToken(self):
        refreshToken = self.__cache.RefreshToken
        if refreshToken == "":
            return ""
        tokenUrl = const.SERVER_HOST + const.TOKEN_URL
        cookie = f"RefreshToken={refreshToken}"
        header = self.__httpServices.CreateNewHttpHeader(cookie = cookie, endProfileId=self.__cache.EndUserId)
        req = self.__httpServices.CreateNewHttpRequest(url=tokenUrl, header=header)
        session = aiohttp.ClientSession()
        res = await self.__httpServices.UsePostRequest(session, req)  
        token = ""
        if res != "":
            try:
                data = await res.json()
                token = data['token']
            except:
                return ""
        await session.close()
        return token  
    
    def __hcUpdateReconnectStToDb(self):
        self.__logger.info("Update cloud reconnect status to db")
        print("Update cloud reconnect status to db")
        s =systemConfiguration(isConnect= True, DisconnectTime= None, ReconnectTime= datetime.datetime.now())
        self.__db.Services.SystemConfigurationServices.AddNewSysConfiguration(s)
        self.__cache.SignalrDisconnectStatusUpdate = False 
        self.__cache.SignalrDisconnectCount = 0
     
    def __hcUpdateDisconnectStToDb(self):
        self.__logger.info("Update cloud disconnect status to db")
        print("Update cloud Disconnect status to db")
        s =systemConfiguration(isConnect= False, DisconnectTime= self.__cache.DisconnectTime, ReconnectTime= None)
        self.__db.Services.SystemConfigurationServices.AddNewSysConfiguration(s)
        self.__cache.SignalrDisconnectStatusUpdate = True
        self.__cache.SignalrDisconnectCount = 0  
    #-----------------------
    
    #------------------Mqtt data handler          
    async def __HcMqttHandlerData(self):
        """ This function handler data received in queue
        """
        while True:
            await asyncio.sleep(0.1)
            if self.__mqttServices.mqttDataQueue.empty() == False:
                with self.__lock:
                    item = self.__mqttServices.mqttDataQueue.get()
                    self.__mqttItemHandler(item)
                    self.__mqttServices.mqttDataQueue.task_done()

    def __mqttItemHandler(self, item):
        try:
            switcher = {
                const.MQTT_SUB_RESPONSE_TOPIC: self.__mqttHandlerHcControlResponse
            }
            func = switcher.get(item["topic"])
            func(item["msg"])
        except:
            pass
        return
    
    def __mqttHandlerHcControlResponse(self, data):
        print(data)
    #---------------------------
    
    #------------------- Signalr data handler
    async def __HcHandlerSignalRData(self):
        while True:
            await asyncio.sleep(0.1)
            if self.__signalServices.signalrDataQueue.empty() == False:
                with self.__lock:
                    try:
                        item = self.__signalServices.signalrDataQueue.get()
                        self.__signalrItemHandler(item)
                        self.__signalServices.signalrDataQueue.task_done()
                    except:
                        pass
        
    def __signalrItemHandler(self, *args):
        try:
            switcher = {
                "Command": self.__signalrHandlerCommand
            }
            func = switcher.get(args[0][0])
            func(args[0][1])
        except:
            pass
        return

    def __signalrHandlerCommand(self, data):
        self.__logger.debug("data receive from cloud: " + data)
        try:
            d = json.loads(data)
            try:
                _ = d['TYPE']
            except:
                self.__mqttServices.Publish(const.MQTT_PUB_CONTROL_TOPIC, data, const.MQTT_QOS)
                self.__logger.debug("Forward data to cloud")
        except:
            self.__logger.debug("Data receiver invalid")
        return
    #------------------------------
  

    #-------------main function
    async def ActionNoDb(self):
        task1 = asyncio.ensure_future(self.__signalServices.Init())
        task2 = asyncio.ensure_future(self.__mqttServices.Init())
        tasks = [task1, task2]
        await asyncio.gather(*tasks)
        return

    async def ActionDb(self):
        task1 = asyncio.ensure_future(self.__HcHandlerSignalRData())
        task2 = asyncio.ensure_future(self.__HcCheckConnectWithCloud())
        task3 = asyncio.ensure_future(self.__HcMqttHandlerData())
        
        tasks = [task1, task2, task3]
        await asyncio.gather(*tasks)
        return
    