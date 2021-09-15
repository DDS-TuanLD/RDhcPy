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
        }
        func = switcher.get(topic)
        func(message)
        return

    def __handler_topic_hc_control_response(self, data):
        if self.__globalVariables.AllowChangeCloudAccountFlag:
            return
        print("data from topic HC.CONTROL.RESPONSE: " + data)
        self.__logger.debug("data from topic HC.CONTROL.RESPONSE: " + data)

        if self.__globalVariables.PingCloudSuccessFlag:

            try:
                json_data = json.loads(data)
                cmd = json_data.get("CMD", "")
                dt = json_data.get("DATA", "")

                self.__hc_check_cmd_and_send_response_to_cloud(cmd, data)

                switcher = {
                    "DEVICE": self.__handler_cmd_device,
                }
                func = switcher.get(cmd)
                func(dt)

            except:
                self.__logger.error("mqtt data receiver in topic HC.CONTROL.RESPONSE invalid")

    def __handler_topic_hc_control(self, data):
        print("data from topic HC.CONTROL: " + data)
        self.__logger.debug("data from topic HC.CONTROL: " + data)

        try:
            json_data = json.loads(data)
            cmd = json_data.get("CMD", "")
            dt = json_data.get("DATA", "")
            switcher = {
                "HC_CONNECT_TO_CLOUD": self.__handler_cmd_hc_connect_to_cloud,
                "RESET_HC": self.__handler_cmd_reset_hc
            }
            func = switcher.get(cmd)
            func(dt)
        except:
            self.__logger.error("mqtt data receiver in topic HC.CONTROL invalid")

    def __handler_cmd_device(self, data):
        if self.__globalVariables.AllowChangeCloudAccountFlag:
            return
        signal_data = []
        try:
            for d in data:
                for i in d["PROPERTIES"]:
                    data_send_to_cloud = {
                        "deviceId": d['DEVICE_ID'],
                        "deviceAttributeId": i['ID'],
                        "value": i['VALUE']
                    }
                    signal_data.append(data_send_to_cloud)
        except:
            self.__logger.debug("data of cmd Device invalid")
            print("data of cmd Device invalid")

        if signal_data:
            send_data = [const.SIGNALR_CLOUD_RESPONSE_ENTITY, json.dumps(signal_data)]
            self.__signalr.send(self.__globalVariables.DormitoryId, send_data)

        if not signal_data:
            self.__logger.debug("have no data to send to cloud via signalr")
            print("have no data to send to cloud via signalr")

    def __handler_cmd_hc_connect_to_cloud(self, data):
        db = Db()
        dormitory_id = data.get("DORMITORY_ID", "")
        refresh_token = data.get("REFRESH_TOKEN", "")

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

    def __handler_cmd_reset_hc(self, data):
        print("Allow to change account, now new account can log in")
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

    def __hc_check_cmd_and_send_response_to_cloud(self, cmd: str, data: str):
        room_response_cmd = ["CREATE_ROOM", "ADD_DEVICE_TO_ROOM", "REMOVE_DEVICE_FROM_ROOM"]
        scene_response_cmd = ["CREATE_SCENE", "EDIT_SCENE"]
        if room_response_cmd.count(cmd) > 0:
            send_data = [const.SIGNALR_APP_ROOM_RESPONSE_ENTITY, data]
            self.__signalr.send(self.__globalVariables.DormitoryId, send_data)
            return

        if scene_response_cmd.count(cmd) > 0:
            send_data = [const.SIGNALR_APP_SCENE_RESPONSE_ENTITY, data]
            self.__signalr.send(self.__globalVariables.DormitoryId, send_data)
            return

        if (room_response_cmd + scene_response_cmd).count(cmd) == 0:
            send_data = [const.SIGNALR_APP_DEVICE_RESPONSE_ENTITY, data]
            self.__signalr.send(self.__globalVariables.DormitoryId, send_data)
            return
