from HcServices.Http import Http
from HcServices.Signalr import Signalr
from HcServices.Mqtt import Mqtt
import asyncio
from Database.Db import Db
import aiohttp
from Cache.GlobalVariables import GlobalVariables
import Constant.constant as const
import datetime
from Model.systemConfiguration import systemConfiguration
import time
from Model.userData import userData
import logging
import threading
import http
import json
from Contracts.ITransport import ITransport
from Contracts.IController import IController
from Helper.System import System, eliminate_current_progress, ping_google
from Contracts.IHandler import IHandler
from Handler.MqttDataHandler import MqttDataHandler
from Handler.SignalrDataHandler import SignalrDataHandler


class RdHc(IController):
    __httpServices: Http
    __signalServices: ITransport
    __mqttServices: ITransport
    __globalVariables: GlobalVariables
    __lock: threading.Lock
    __logger: logging.Logger
    __mqttHandler: IHandler
    __signalrHandler: IHandler

    def __init__(self, log: logging.Logger, http: Http, signalr: ITransport, mqtt: ITransport,
                 mqtt_handler: IHandler, signalr_handler: IHandler):
        self.__logger = log
        self.__httpServices = http
        self.__signalServices = signalr
        self.__mqttServices = mqtt
        self.__globalVariables = GlobalVariables()
        self.__lock = threading.Lock()
        self.__mqttHandler = mqtt_handler
        self.__signalrHandler = signalr_handler

    async def __hc_check_connect_with_cloud(self):
        s = System(self.__logger)
        signalr_disconnect_count = 0
        request_time_count = 0
        first_success_ping_to_cloud_flag = False
        ok = False

        while True:
            print("Hc send heartbeat to cloud")
            self.__logger.info("Hc send heartbeat to cloud")
            request_time_count = datetime.datetime.now().timestamp()
            if self.__globalVariables.DisconnectTime is None:
                self.__globalVariables.DisconnectTime = datetime.datetime.now()
            rel = ping_google()
            if not rel:
                ok = False
            if rel:
                ok = await s.send_http_request_to_heartbeat_url(self.__httpServices)
            if not ok:
                print("can not ping to cloud")
                self.__hc_check_request_timeout(request_time_count)
                request_time_count = 0
                signalr_disconnect_count = signalr_disconnect_count + 1
                self.__globalVariables.SignalrConnectSuccessFlag = False
                self.__globalVariables.PingCloudSuccessFlag = False
            if ok:
                await s.recheck_reconnect_status_of_last_activation()
                if not first_success_ping_to_cloud_flag:
                    first_success_ping_to_cloud_flag = True
                self.__globalVariables.PingCloudSuccessFlag = True
                self.__globalVariables.DisconnectTime = None
                signalr_disconnect_count = 0
            await asyncio.sleep(15)
            if (signalr_disconnect_count == 12) and (not self.__globalVariables.SignalrDisconnectStatusUpdateStatusFlag):
                self.__hc_update_disconnect_status_to_db()
                if first_success_ping_to_cloud_flag:
                    eliminate_current_progress()

    def __hc_check_request_timeout(self, request_time_count: float):
        if 60 > datetime.datetime.now().timestamp() - request_time_count > 30:
            self.__hc_update_disconnect_status_to_db()
        if datetime.datetime.now().timestamp() - request_time_count > 60:
            self.__hc_update_disconnect_status_to_db()
            eliminate_current_progress()

    async def __hc_update_reconnect_status_to_db(self):
        self.__logger.info("Update cloud reconnect status to db")
        print("Update cloud reconnect status to db")
        s = System(self.__logger)
        await s.update_reconnect_status_to_db(datetime.datetime.now())

    def __hc_update_disconnect_status_to_db(self):
        self.__logger.info("Update cloud disconnect status to db")
        print("Update cloud disconnect status to db")
        s = System(self.__logger)
        s.update_disconnect_status_to_db(self.__globalVariables.DisconnectTime)

    async def __hc_handler_mqtt_data(self):
        while True:
            await asyncio.sleep(0.1)
            if not self.__mqttServices.receive_data_queue.empty():
                with self.__lock:
                    item = self.__mqttServices.receive_data_queue.get()
                    self.__mqttHandler.handler(item)
                    self.__mqttServices.receive_data_queue.task_done()

    async def __hc_handler_signalr_data(self):
        while True:
            await asyncio.sleep(0.1)
            if not self.__signalServices.receive_data_queue.empty():
                with self.__lock:
                    item = self.__signalServices.receive_data_queue.get()
                    self.__signalrHandler.handler(item)
                    self.__signalServices.receive_data_queue.task_done()

    def __hc_load_user_data(self):
        db = Db()
        user_data = db.Services.UserdataServices.FindUserDataById(id=1)
        dt = user_data.first()
        if dt is not None:
            self.__globalVariables.EndUserId = dt["EndUserProfileId"]
            self.__globalVariables.RefreshToken = dt["RefreshToken"]

    async def run(self):
        self.__hc_load_user_data()
        self.__mqttServices.connect()
        task0 = asyncio.create_task(self.__signalServices.connect())
        task1 = asyncio.create_task(self.__hc_handler_signalr_data())
        task2 = asyncio.create_task(self.__hc_check_connect_with_cloud())
        task3 = asyncio.create_task(self.__hc_handler_mqtt_data())
        tasks = [task0, task1, task2, task3]
        await asyncio.gather(*tasks)
