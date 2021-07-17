from Contracts.Ihandler import Ihandler
import asyncio
import logging
from HcServices.Mqtt import Mqtt
from HcServices.Signalr import Signalr
from Contracts.Itransport import Itransport
from Cache.GlobalVariables import GlobalVariables
import Constant.constant as const
import json
from Database.Db import Db
from Model.systemConfiguration import systemConfiguration
from Model.userData import userData
from Helper.System import System


class MqttDataHandler(Ihandler):
    __logger: logging.Logger
    __mqtt: Itransport
    __signalr: Itransport
    __db: Db
    __globalVariables: GlobalVariables
    
    def __init__(self, log: logging.Logger, mqtt: Itransport, signalr: Itransport):
        self.__logger = log
        self.__mqtt = mqtt
        self.__db = Db()
        self.__globalVariables = GlobalVariables()
        self.__signalr = signalr
        
    def Handler(self, item):
        switcher = {
            const.MQTT_RESPONSE_TOPIC: self.__handlerTopicHcControlResponse,
            const.MQTT_CONTROL_TOPIC: self.__handlerTopicHcControl,
            "test": self.__test,
        }
        func = switcher.get(item["topic"])
        func(item["msg"])
        return

    async def __checkAndReconnectSignalrWhenHaveInternet(self):
        s = System(self.__logger)
        while not s.PingGoogle():
            await asyncio.sleep(2)
        while not self.__globalVariables.PingCloudSuccessFlag:
            await asyncio.sleep(2)
        await self.__signalr.DisConnect()
        self.__signalr.ReConnect()
        self.__globalVariables.NeedReconnectSignalrServerFlag = False

    def __test(self, data):
        loop = asyncio.get_running_loop()
        loop.create_task(self.__checkAndReconnectSignalrWhenHaveInternet())

    def __handlerTopicHcControlResponse(self, data):
        print("data from topic HC.CONTROL.RESPONSE: " + data)
        self.__logger.debug("data from topic HC.CONTROL.RESPONSE: " + data)

        if self.__globalVariables.PingCloudSuccessFlag:
            self.__signalr.Send(endUserProfileId=self.__globalVariables.EndUserId, entity=const.SIGNALR_APP_RESPONSE_ENTITY, message=data)
            
            try:
                dt = json.loads(data)
                try:
                    cmd = dt["CMD"]
                    data = dt["DATA"]
                    switcher = {
                        "DEVICE": self.__handlerCmdDevice
                    }
                    func = switcher.get(cmd)
                    func(data)
                except:
                    self.__logger.error("mqtt data receiver in topic HC.CONTROL.RESPONSE invalid")
            except:
                self.__logger.error("mqtt data receiver in topic HC.CONTROL.RESPONSE invalid")
       
    def __handlerTopicHcControl(self, data):
        print("data from topic HC.CONTROL: " + data)
        self.__logger.debug("data from topic HC.CONTROL: " + data)
        
        try:
            dt = json.loads(data)
            try:
                cmd = dt["CMD"]
                data = dt["DATA"]
                switcher = {
                    "HC_CONNECT_TO_CLOUD": self.__handlerCmdHcConnectToCloud
                }
                func = switcher.get(cmd)
                func(data)
            except:
                self.__logger.error("mqtt data receiver in topic HC.CONTROL invalid")
        except:
            self.__logger.error("mqtt data receiver in topic HC.CONTROL invalid")
          
    def __handlerCmdDevice(self, data):
        signal_data = []
        try:
            for i in range(len(data['PROPERTIES'])):
                d = {
                    "deviceId": data['DEVICE_ID'],
                    "deviceAttributeId": data['PROPERTIES'][i]['ID'],
                    "value": data['PROPERTIES'][i]['VALUE']
                }
                signal_data.append(d)
        except:
            self.__logger.debug("data of cmd Device invalid")
            print("data of cmd Device invalid")
        
        if signal_data:
            self.__signalr.Send(endUserProfileId=self.__globalVariables.EndUserId, entity=const.SIGNALR_CLOUD_RESPONSE_ENTITY, message=json.dumps(signal_data))
        
        if not signal_data:
            self.__logger.debug("have no data to send to cloud via signalr")
            print("have no data to send to cloud via signalr")              
          
    def __handlerCmdHcConnectToCloud(self, data):
        try:
            endUserProfileId = data["END_USER_PROFILE_ID"]
            refreshToken = data["REFRESH_TOKEN"]
            if self.__globalVariables.EndUserId != str(endUserProfileId) and self.__globalVariables.EndUserId != "":
                return
            if self.__globalVariables.EndUserId == "":
                self.__globalVariables.EndUserId = str(endUserProfileId)
                self.__globalVariables.RefreshToken = refreshToken
                return
            self.__globalVariables.EndUserId = str(endUserProfileId)
            self.__globalVariables.RefreshToken = refreshToken
            userDt = userData(refreshToken=refreshToken, endUserProfileId=str(endUserProfileId))
            rel = self.__db.Services.UserdataServices.FindUserDataById(id = 1)
            dt = rel.first()
            if dt is not None:
                self.__db.Services.UserdataServices.UpdateUserDataById(id = 1, newUserData=userDt)
            if dt is None:
                self.__db.Services.UserdataServices.AddNewUserData(newUserData=userDt)
            
            if self.__globalVariables.PingCloudSuccessFlag:
                self.__globalVariables.ResetSignalrConnectFlag = True
        except:
            self.__logger.error("data of cmd HcConnectToCLoud invalid")
            print("data of cmd HcConnectToCLoud invalid")
