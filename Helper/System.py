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

class System():
    __db=Db()
    __cache=Cache()
    
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
        s =systemConfiguration(isConnect= True, DisconnectTime= r['DisconnectTime'], ReconnectTime= reconnectTime, isSync=False)
        self.__db.Services.SystemConfigurationServices.UpdateSysConfigurationById(id=1, sysConfig=s)
        self.__cache.SignalrDisconnectStatusUpdate = False 
        self.__cache.SignalrDisconnectCount = 0
        await self.PushDataToCloud(referenceTime=r['DisconnectTime'])
        
    def UpdateDisconnectStatusToDb(self, DisconnectTime: datetime.datetime):
        s =systemConfiguration(isConnect= False, DisconnectTime= DisconnectTime, ReconnectTime= None, isSync=False)
        rel = self.__db.Services.SystemConfigurationServices.FindSysConfigurationById(id=1)
        r = rel.first()
        if r == None:
            self.__db.Services.SystemConfigurationServices.AddNewSysConfiguration(s)
        if r!=None and r["IsSync"]!="False":
            self.__db.Services.SystemConfigurationServices.UpdateSysConfigurationById(id=1, sysConfig=s)
        self.__cache.SignalrDisconnectStatusUpdate = True
        self.__cache.SignalrDisconnectCount = 0  
    
    async def RecheckReconnectStatusOfLastActiveInDb(self):
        if self.__cache.RecheckConnectionStatusInDb == False:
            rel = self.__db.Services.SystemConfigurationServices.FindSysConfigurationById(id=1)
            r = rel.first()
            if r["ReconnectTime"] == None:
                s = System()
                await s.UpdateReconnectStatusToDb(reconnectTime=datetime.datetime.now())
            self.__cache.RecheckConnectionStatusInDb = True  
            
    def SendCommandOverMqtt(self, mqtt: Mqtt, topic: str, cmd: str, qos: int):
        mqtt.Send(topic=topic, send_data=cmd, qos=qos)  
            
    async def PushDataToCloud(self, referenceTime: datetime.datetime):
        t = self.__timeSplit(time=referenceTime)
        updateDay = t[0]
        updateTime = t[1]
        rel = self.__db.Services.DeviceAttributeValueServices.FindDeviceAttributeValueWithCondition(or_(and_(self.__db.Table.DeviceAttributeValueTable.c.UpdateDay == updateDay, self.__db.Table.DeviceAttributeValueTable.c.UpdateTime >= updateTime), self.__db.Table.DeviceAttributeValueTable.c.UpdateDay > updateDay))

        data = []
        for r in rel:
            d = {
                "deviceId": r['DeviceId'],
                "deviceAttributeId": r['DeviceAttributeId'],
                "value": r['Value']
            }
            data.append(d)
        dt = json.dumps(data)
        print(dt)
        h = Http()
        token = await self.__getToken(h) 
        cookie = f"Token={token}"
        pullDataUrl = const.SERVER_HOST + const.CLOUD_PUSH_DATA_URL
        header = h.CreateNewHttpHeader(cookie = cookie, endProfileId=self.__cache.EndUserId)
        req = h.CreateNewHttpRequest(url=pullDataUrl, body_data=json.loads(dt) , header=header)
        session = aiohttp.ClientSession()
        res = await h.Post(session, req)
        await session.close()
        print(res)
        if res == "":
            return False
        if (res != "") and (res.status == http.HTTPStatus.OK):
            self.__updateAsyncStatusSuccessToDb()
            print("Update to cloud ok")
            return True
       
    def __updateAsyncStatusSuccessToDb(self):
        rel = self.__db.Services.SystemConfigurationServices.FindSysConfigurationById(id=1)
        r = rel.first()
        s =systemConfiguration(isConnect= r['IsConnect'], DisconnectTime= r['DisconnectTime'], ReconnectTime= r['ReconnectTime'], isSync=True)
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