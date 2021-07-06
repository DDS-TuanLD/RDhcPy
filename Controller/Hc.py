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

class RdHc(IController):
    __httpServices: Http
    __signalServices: Itransport
    __mqttServices: Itransport
    __db: Db
    __cache : Cache
    __lock: threading.Lock
    __logger: logging.Logger

    def __init__(self, log: logging.Logger):
        self.__logger = log
        self.__httpServices = Http()
        self.__signalServices = Signalr(self.__logger)
        self.__mqttServices = Mqtt(self.__logger)
        self.__db = Db()
        self.__cache = Cache()
        self.__lock = threading.Lock()
           
    async def __HcUpdateUserdata(self):
       pass
            
    #-----------------Ping cloud----------------------------------------------------------------------
    async def __HcCheckConnectWithCloud(self):
        s = System()
        while True:  
            print("Hc send heardbeat to cloud")
            self.__logger.info("Hc send heardbeat to cloud")
            if self.__cache.DisconnectTime == None:
                self.__cache.DisconnectTime = datetime.datetime.now()
            ok = await self.__hcSendHttpRequestToHeardbeatUrl()
            if ok == False:
                self.__cache.SignalrDisconnectCount = self.__cache.SignalrDisconnectCount + 1 
                self.__cache.signalrConnectSuccess = False 
                self.__cache.pingCloudHttp = False
            if ok == True:
                await s.RecheckReconnectStatusOfLastActiveInDb()
                # if self.__cache.FirstPullDataToCloud == False:
                #     s.PushDataToCloud(http=self.__httpServices, referenceTime=datetime.datetime.now())
                #     self.__cache.FirstPullDataToCloud = True
                self.__cache.pingCloudHttp = True
                self.__cache.DisconnectTime = None
                if self.__cache.signalrConnectSuccess == False: 
                    self.__signalServices.ReConnect()
                    self.__cache.signalrConnectSuccess = True
            if (ok == True) and (self.__cache.SignalrDisconnectStatusUpdate == True):
                await self.__hcUpdateReconnectStToDb()
            await asyncio.sleep(30)
            if (self.__cache.SignalrDisconnectCount == 3) and (self.__cache.SignalrDisconnectStatusUpdate == False):
                self.__hcUpdateDisconnectStToDb()
                self.__cache.SignalrDisconnectCount = 0
                
    async def __hcSendHttpRequestToHeardbeatUrl(self):
        endUser = self.__cache.EndUserId
        token = await self.__hcGetToken() 
        cookie = f"Token={token}"
        heardBeatUrl = const.SERVER_HOST + const.SIGNSLR_HEARDBEAT_URL
        header = self.__httpServices.CreateNewHttpHeader(cookie = cookie, endProfileId=self.__cache.EndUserId)
        req = self.__httpServices.CreateNewHttpRequest(url=heardBeatUrl, header=header)
        session = aiohttp.ClientSession()
        res = await self.__httpServices.Post(session, req)
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
        res = await self.__httpServices.Post(session, req)  
        token = ""
        if res != "":
            try:
                data = await res.json()
                token = data['token']
            except:
                return ""
        await session.close()
        return token  
    
    async def __hcUpdateReconnectStToDb(self):
        self.__logger.info("Update cloud reconnect status to db")
        print("Update cloud reconnect status to db")
        s = System()
        await s.UpdateReconnectStatusToDb(reconnectTime=datetime.datetime.now())
        
    def __hcUpdateDisconnectStToDb(self):
        self.__logger.info("Update cloud disconnect status to db")
        print("Update cloud disconnect status to db")
        s = System()
        s.UpdateDisconnectStatusToDb(DisconnectTime=self.__cache.DisconnectTime) 
    #--------------------------------------------------------------------------------------
    
    #------------------Mqtt data handler---------------------------------------------------         
    async def __HcMqttHandlerData(self):
        """ This function handler data received in queue
        """
        while True:
            await asyncio.sleep(0.1)
            if self.__mqttServices.mqttDataQueue.empty() == False:
                with self.__lock:
                    item = self.__mqttServices.mqttDataQueue.get()
                    await self.__hcMqttItemHandler(item)
                    self.__mqttServices.mqttDataQueue.task_done()

    async def __hcMqttItemHandler(self, item):
        try:
            switcher = {
                const.MQTT_SUB_RESPONSE_TOPIC: self.__mqttHandlerHcControlResponse,
                const.MQTT_PUB_CONTROL_TOPIC: self.__mqttHandlerTopicHcControl
            }
            func = switcher.get(item["topic"])
            await func(item["msg"])
        except:
            pass
        return
    
    async def __mqttHandlerHcControlResponse(self, data):
        self.__signalServices.Send(endUserProfileId=self.__cache.EndUserId, entity="Command", message=data)
    
    async def __mqttHandlerTopicHcControl(self, data):
        try:
            dt = json.loads(data)
            try:
                cmd = dt["CMD"]
                data = dt["DATA"]
                switcher = {
                    "HC_CONNECT_TO_CLOUD": self.__mqttHandlerCmdConnectToCloud
                }
                func = switcher.get("HC_CONNECT_TO_CLOUD")
                await func(data)
            except:
                self.__logger.error("mqtt data receiver invalid")
        except:
            self.__logger.error("mqtt data receiver invalid")
          
    async def __mqttHandlerCmdConnectToCloud(self, data):
        try:
            endUserProfileId = data["END_USER_PROFILE_ID"]
            refreshToken = data["REFRESH_TOKEN"]
            self.__cache.EndUserId = str(endUserProfileId)
            self.__cache.RefreshToken = refreshToken
            userDt = userData(refreshToken=refreshToken, endUserProfileId=str(endUserProfileId))
            rel = self.__db.Services.UserdataServices.FindUserDataById(id = 1)
            dt = rel.first()
            if dt != None:
                self.__db.Services.UserdataServices.UpdateUserDataById(id = 1, newUserData=userDt)
            if dt == None:
                self.__db.Services.UserdataServices.AddNewUserData(newUserData=userDt)
            
            if self.__cache.pingCloudHttp == True:
                await self.__signalServices.DisConnect()
                self.__signalServices.ReConnect()
        except:
            self.__logger.error("mqtt data receiver invalid")
    #------------------------------------------------------------------------------------------------
    
    #------------------- Signalr data handler--------------------------------------------------------
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
            self.__logger.debug(f"handler receive signal data in {args[0][0]} is {args[0][1]}")
            print(f"handler receive signal data in {args[0][0]} is {args[0][1]}")
            switcher = {
                "Command": self.__signalrHandlerCommand
            }
            func = switcher.get(args[0][0])
            func(args[0][1])
        except:
            pass
        return

    def __signalrHandlerCommand(self, data):
        try:
            print(f"Forward data to mqtt: {data}")
            self.__mqttServices.Send(const.MQTT_PUB_CONTROL_TOPIC, data, const.MQTT_QOS)
            self.__logger.debug("Forward data to mqtt")
        except:
            self.__logger.debug("Data receiver invalid")
        return
    #------------------------------------------------------------------------------------------
  
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
        task3 = asyncio.ensure_future(self.__HcMqttHandlerData())     
        tasks = [task1, task2, task3]
        await asyncio.gather(*tasks)
        return
    