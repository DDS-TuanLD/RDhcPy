from Helper.Terminal import Terminal
from Database.Db import Db
from Model.systemConfiguration import systemConfiguration
from Cache.Cache import Cache
import datetime
from HcServices.Mqtt import Mqtt
from HcServices.Http import Http
from sqlalchemy import and_, or_
from HcServices.Http import Http
import aiohttp
import asyncio
import Constant.constant as const
import http
import json
import logging

class System():
    __db=Db()
    __cache=Cache()
    __logger = logging.Logger
    
    def __init__(self, logger: logging.Logger):
        self.__logger = logger
    
    def EliminateCurrentProgess(self):
        t = Terminal()
        s = t.ExecuteWithResult(f'ps | grep python3')
        dt = s[1].split(" ")
        for i in range(len(dt)):
            if dt[i] != "":
                print(dt[i])
                break
        s = t.Execute(f'kill -9 {dt[i]}')
    
    async def UpdateReconnectStatusToDb(self, reconnectTime: datetime.datetime):
        rel = self.__db.Services.SystemConfigurationServices.FindSysConfigurationById(id=1)
        r = rel.first()
        s =systemConfiguration(IsConnect= True, DisconnectTime= r['DisconnectTime'], ReconnectTime= reconnectTime, IsSync=r['IsSync'])
        self.__db.Services.SystemConfigurationServices.UpdateSysConfigurationById(id=1, sysConfig=s)
        await self.__pushDataToCloud(referenceTime=r['DisconnectTime'], dt=s)
      
    def UpdateDisconnectStatusToDb(self, DisconnectTime: datetime.datetime):
        s =systemConfiguration(IsConnect= False, DisconnectTime= DisconnectTime, ReconnectTime= None, IsSync=False)
        rel = self.__db.Services.SystemConfigurationServices.FindSysConfigurationById(id=1)
        r = rel.first()
        if r == None:
            self.__db.Services.SystemConfigurationServices.AddNewSysConfiguration(s)
        if r!=None and r["IsSync"]!="False":
            self.__db.Services.SystemConfigurationServices.UpdateSysConfigurationById(id=1, sysConfig=s)
           
    async def RecheckReconnectStatusOfLastActiveInDb(self):
        if self.__cache.RecheckConnectionStatusInDbFlag == False:
            rel = self.__db.Services.SystemConfigurationServices.FindSysConfigurationById(id=1)
            r = rel.first()
            
            if r == None:
                s = systemConfiguration(IsConnect=True, DisconnectTime=datetime.datetime.now(), ReconnectTime=datetime.datetime.now(), IsSync=True)
                self.__db.Services.SystemConfigurationServices.AddNewSysConfiguration(s)
                self.__cache.RecheckConnectionStatusInDbFlag = True
                return
                
            s =systemConfiguration(IsConnect= r["IsConnect"], DisconnectTime= r['DisconnectTime'], ReconnectTime= r['ReconnectTime'], IsSync=r['IsSync'])

            if r["ReconnectTime"] == None:
                await self.UpdateReconnectStatusToDb(reconnectTime=datetime.datetime.now())
                return  

            if r["ReconnectTime"] != None and r["IsSync"] == "False":
                ok = await self.__pushDataToCloud(referenceTime=r["DisconnectTime"], dt=s)
                if ok == True:
                    self.__cache.RecheckConnectionStatusInDbFlag = True 
                return
        self.__cache.RecheckConnectionStatusInDbFlag = True
        return
     
    async def SendHttpRequestToHeardbeatUrl(self, h: Http):
        endUser = self.__cache.EndUserId
        token = await self.__getToken(h) 
        cookie = f"Token={token}"
        heardBeatUrl = const.SERVER_HOST + const.SIGNSLR_HEARDBEAT_URL
        header = h.CreateNewHttpHeader(cookie = cookie, endProfileId=self.__cache.EndUserId)
        req = h.CreateNewHttpRequest(url=heardBeatUrl, header=header)
        session = aiohttp.ClientSession()
        res = await h.Post(session, req)
        await session.close()
        if res == "":
            return False
        if (res != "") and (res.status == http.HTTPStatus.OK):
            return True
        
    async def __getToken(self, http: Http):
        refreshToken = self.__cache.RefreshToken
        if refreshToken == "":
            return ""
        tokenUrl = const.SERVER_HOST + const.TOKEN_URL
        cookie = f"RefreshToken={refreshToken}"
        header = http.CreateNewHttpHeader(cookie = cookie, endProfileId=self.__cache.EndUserId)
        req = http.CreateNewHttpRequest(url=tokenUrl, header=header)
        session = aiohttp.ClientSession()
        res = await http.Post(session, req)  
        token = ""
        if res != "":
            try:
                data = await res.json()
                token = data['token']
            except:
                return ""
        await session.close()
        return token 
    
    async def __pushDataToCloud(self, referenceTime: datetime.datetime, dt: systemConfiguration):
        t = self.__timeSplit(time=referenceTime)
        updateDay = t[0]
        updateTime = t[1]
        print(f"updateDay: {updateDay}, updateTime: {updateTime}")
        rel = self.__db.Services.DeviceAttributeValueServices.FindDeviceAttributeValueWithCondition(or_(and_(self.__db.Table.DeviceAttributeValueTable.c.UpdateDay == updateDay, self.__db.Table.DeviceAttributeValueTable.c.UpdateTime >= updateTime), self.__db.Table.DeviceAttributeValueTable.c.UpdateDay > updateDay))
        data = []
        for r in rel:
            if r['DeviceId'] == "" or r['DeviceAttributeId'] == None or r['Value'] == None:
                continue
            d = {
                "deviceId": r['DeviceId'],
                "deviceAttributeId": r['DeviceAttributeId'],
                "value": r['Value']
            }
            data.append(d)
        if data == []:
            print("hava no data to push")
            self.__logger.info("hava no data to push")
            self.__updateSyncDataStatusSuccessToDb(dt)
            return True
        data_send_to_cloud = json.dumps(data)
        print(f"push data: {data_send_to_cloud}")
        res = await self.__sendHttpRequestToPushUrl(data=data_send_to_cloud)
        if res == "":
            print("Push data failure")
            self.__logger.info("Push data failure")
            self.__updateSyncDataStatusFailToDb(dt)
            return False
        if (res != "") and (res.status == http.HTTPStatus.OK):
            self.__updateSyncDataStatusSuccessToDb(dt)
            print("Push data successfully")
            self.__logger.info("Push data successfully")
            return True
    
    async def __sendHttpRequestToPushUrl(self, data: list):
        h = Http()
        token = await self.__getToken(h) 
        cookie = f"Token={token}"
        print(f"cookie: {cookie}")
        pullDataUrl = const.SERVER_HOST + const.CLOUD_PUSH_DATA_URL
        header = h.CreateNewHttpHeader(cookie = cookie, endProfileId=self.__cache.EndUserId)
        req = h.CreateNewHttpRequest(url=pullDataUrl, body_data=json.loads(data) , header=header)
        session = aiohttp.ClientSession()
        res = await h.Post(session, req)
        await session.close()
        print(res)

       
    def __updateSyncDataStatusSuccessToDb(self, s: systemConfiguration):
        s.IsSync = True
        self.__db.Services.SystemConfigurationServices.UpdateSysConfigurationById(id=1, sysConfig=s)
        
    def __updateSyncDataStatusFailToDb(self, s: systemConfiguration):
        s.IsSync = False
        self.__db.Services.SystemConfigurationServices.UpdateSysConfigurationById(id=1, sysConfig=s)
        
    def __timeSplit(self, time: datetime.datetime):
        m = str(time.month)
        if int(m) < 10:
            m = "0"+ m
            
        d = str(time.day)
        if int(d) < 10:
            d = "0" + d
            
        updateDay = int(str(time.year) + m + d)
        updateTime = 60*time.hour + time.minute
        return updateDay, updateTime
    
    