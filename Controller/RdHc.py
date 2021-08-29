from HcServices.Http import Http
import asyncio
from Database.Db import Db
from Cache.GlobalVariables import GlobalVariables
import datetime
import logging
import threading
from Contracts.ITransport import ITransport
from Contracts.IController import IController
from Helper.System import System, eliminate_current_progress, ping_google, check_and_kill_all_repeat_progress
from Contracts.IHandler import IHandler
from Helper.Terminal import execute_with_result, execute


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

    async def __hc_check_connect_with_internet(self):
        google_disconnect_count = 0
        while True:
            self.__globalVariables.PingGoogleSuccessFlag = ping_google()
            
            if not self.__globalVariables.PingGoogleSuccessFlag:
                google_disconnect_count = google_disconnect_count + 1
            if self.__globalVariables.PingGoogleSuccessFlag:
                google_disconnect_count = 0
            if google_disconnect_count == 3:
                self.__hc_update_disconnect_status_to_db()
                eliminate_current_progress()
                
            await asyncio.sleep(10)

    async def __hc_check_connect_with_cloud(self):
        s = System(self.__logger)
        signalr_disconnect_count = 0
        request_time_count = 0
        first_success_ping_to_cloud_flag = False

        while True:
            print("Hc send heartbeat to cloud")
            self.__logger.info("Hc send heartbeat to cloud")
            
            await asyncio.sleep(60)

            request_time_count = datetime.datetime.now().timestamp()
            if self.__globalVariables.DisconnectTime is None:
                self.__globalVariables.DisconnectTime = datetime.datetime.now()

            if not self.__globalVariables.PingGoogleSuccessFlag:
                self.__globalVariables.PingCloudSuccessFlag = False
            if self.__globalVariables.PingGoogleSuccessFlag:
                self.__globalVariables.PingCloudSuccessFlag = \
                    await s.send_http_request_to_heartbeat_url(self.__httpServices)

            if not self.__globalVariables.PingCloudSuccessFlag:
                print("can not ping to cloud")
                self.__logger.info("can not ping to cloud")

                self.__hc_check_request_timeout(request_time_count)
                request_time_count = 0
                signalr_disconnect_count = signalr_disconnect_count + 1
                self.__globalVariables.SignalrConnectSuccessFlag = False

            if self.__globalVariables.PingCloudSuccessFlag:
                await s.recheck_reconnect_status_of_last_activation()
                if not first_success_ping_to_cloud_flag:
                    first_success_ping_to_cloud_flag = True
                self.__globalVariables.DisconnectTime = None
                signalr_disconnect_count = 0
                
            if (signalr_disconnect_count == 3) and (not self.__globalVariables.SignalrDisconnectStatusUpdateFlag):
                self.__hc_update_disconnect_status_to_db()
                if first_success_ping_to_cloud_flag:
                    self.__logger.info("program had been eliminated")
                    print("program had been eliminated")
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
            self.__globalVariables.DormitoryId = dt["DormitoryId"]
            self.__globalVariables.RefreshToken = dt["RefreshToken"]
            self.__globalVariables.AllowChangeCloudAccountFlag = dt["AllowChangeAccount"]

    def __hc_load_current_wifi_name(self):
        s = System(self.__logger)
        s.update_current_wifi_name()

    async def __hc_check_wifi_change(self):
        s = System(self.__logger)
        while True:
            await asyncio.sleep(2)
            await s.check_wifi_change(self.__signalServices)

    async def run(self):
        check_and_kill_all_repeat_progress()
        self.__hc_load_user_data()
        self.__hc_load_current_wifi_name()
        self.__mqttServices.connect()
        task0 = asyncio.create_task(self.__signalServices.connect())
        task1 = asyncio.create_task(self.__hc_handler_signalr_data())
        task2 = asyncio.create_task(self.__hc_check_connect_with_cloud())
        task3 = asyncio.create_task(self.__hc_handler_mqtt_data())
        task4 = asyncio.create_task(self.__hc_check_connect_with_internet())
        task5 = asyncio.create_task(self.__hc_check_wifi_change())
        tasks = [task0, task1, task2, task3, task4]
        await asyncio.gather(*tasks)
