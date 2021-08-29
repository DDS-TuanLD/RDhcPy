from Contracts.IHandler import IHandler
import asyncio
import logging
from Contracts.ITransport import ITransport
from Cache.GlobalVariables import GlobalVariables
import Constant.constant as const
import json
from Database.Db import Db
from Model.userData import userData
from Helper.System import System, ping_google


class MqttDataHandler(IHandler):
    __logger: logging.Logger
    __mqtt: ITransport
    __signalr: ITransport
    __globalVariables: GlobalVariables

    def __init__(self, log: logging.Logger, mqtt: ITransport, signalr: ITransport):
        self.__logger = log
        self.__mqtt = mqtt
        self.__globalVariables = GlobalVariables()
        self.__signalr = signalr

    def handler(self, item):
        topic = item['topic']
        message = item['msg']
        switcher = {
            const.MQTT_RESPONSE_TOPIC: self.__handler_topic_hc_control_response,
            const.MQTT_CONTROL_TOPIC: self.__handler_topic_hc_control,
            "aaabbbccc": self.__test,
        }
        func = switcher.get(topic)
        func(message)
        return

    async def __check_and_reconnect_signalr_when_have_internet(self):
        s = System(self.__logger)
        while not ping_google():
            await asyncio.sleep(2)
        while not self.__globalVariables.PingCloudSuccessFlag:
            await asyncio.sleep(2)
        await self.__signalr.disconnect()
        self.__signalr.reconnect()
        self.__globalVariables.NeedReconnectSignalrServerFlag = False

    def __test(self, data):
        loop = asyncio.get_running_loop()
        loop.create_task(self.__check_and_reconnect_signalr_when_have_internet())

    def __handler_topic_hc_control_response(self, data):
        print("data from topic HC.CONTROL.RESPONSE: " + data)
        self.__logger.debug("data from topic HC.CONTROL.RESPONSE: " + data)

        if self.__globalVariables.PingCloudSuccessFlag:
            send_data = [const.SIGNALR_APP_RESPONSE_ENTITY, data]
            self.__signalr.send(self.__globalVariables.DormitoryId, send_data)
            
            cmd: str
            data: str

            try:
                dt = json.loads(data)
                try:
                    cmd = dt["CMD"]
                except:
                    cmd = ""

                try:
                    data = dt["DATA"]
                except:
                    data = ""

                switcher = {
                    "DEVICE": self.__handler_cmd_device,
                    "RESET_HC": self.__handler_cmd_hc_disconnect_with_app
                }
                func = switcher.get(cmd)
                func(data)
            except:
                self.__logger.error("mqtt data receiver in topic HC.CONTROL.RESPONSE invalid")

    def __handler_topic_hc_control(self, data):
        print("data from topic HC.CONTROL: " + data)
        self.__logger.debug("data from topic HC.CONTROL: " + data)
        cmd: str
        data: str

        try:
            dt = json.loads(data)
            try:
                cmd = dt["CMD"]
            except:
                cmd = ""

            try:
                data = dt["DATA"]
            except:
                data = ""

            switcher = {
                "HC_CONNECT_TO_CLOUD": self.__handler_cmd_hc_connect_to_cloud,
            }
            func = switcher.get(cmd)
            func(data)
        except:
            self.__logger.error("mqtt data receiver in topic HC.CONTROL invalid")

    def __handler_cmd_device(self, data):
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
            
        print(signal_data)

        if signal_data:
            send_data = [const.SIGNALR_CLOUD_RESPONSE_ENTITY, json.dumps(signal_data)]
            self.__signalr.send(self.__globalVariables.DormitoryId, send_data)

        if not signal_data:
            self.__logger.debug("have no data to send to cloud via signalr")
            print("have no data to send to cloud via signalr")

    def __handler_cmd_hc_connect_to_cloud(self, data):
        db = Db()
        dormitory_id: str
        refresh_token: str

        try:
            dormitory_id = data["DORMITORY_ID"]
        except:
            dormitory_id = ""

        try:
            refresh_token = data["REFRESH_TOKEN"]
        except:
            refresh_token = ""

        if not self.__globalVariables.AllowChangeCloudAccountFlag and self.__globalVariables.DormitoryId != "":
            return

        if refresh_token != "":
            self.__globalVariables.RefreshToken = refresh_token
        self.__globalVariables.DormitoryId = dormitory_id

        self.__globalVariables.AllowChangeCloudAccountFlag = False

        user_data = userData(refreshToken=refresh_token, dormitoryId=dormitory_id, allowChangeAccount=False)
        rel = db.Services.UserdataServices.FindUserDataById(id=1)
        dt = rel.first()
        if dt is not None:
            db.Services.UserdataServices.UpdateUserDataById(id=1, newUserData=user_data)
        if dt is None:
            db.Services.UserdataServices.AddNewUserData(newUserData=user_data)
            return
        
        self.__globalVariables.ResetSignalrConnectFlag = True

    def __handler_cmd_hc_disconnect_with_app(self, data):
        print("Allow to change account")
        self.__logger.info("Allow to change account, now new account can log in")
        db = Db()
        self.__globalVariables.AllowChangeCloudAccountFlag = True

        rel = db.Services.UserdataServices.FindUserDataById(id=1)
        dt = rel.first()
        if dt is None:
            return

        user_data = userData(refreshToken=self.__globalVariables.RefreshToken,
                             dormitoryId=self.__globalVariables.DormitoryId,
                             allowChangeAccount=self.__globalVariables.AllowChangeCloudAccountFlag)
        db.Services.UserdataServices.UpdateUserDataById(id=1, newUserData=user_data)