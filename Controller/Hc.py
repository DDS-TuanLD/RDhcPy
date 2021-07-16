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
    __cache: Cache
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
        self.__mqttHandler = MqttDataHandler(self.__logger, self.__mqttServices, self.__signalServices)
        self.__signalrHandler = SignalrDataHandler(self.__logger, self.__mqttServices, self.__signalServices)

    async def __HcCheckConnectWithCloud(self):
        s = System(self.__logger)
        signalrDisconnectCount = 0
        requestTimeCount = 0
        firstPingSuccessToCloudFlag = False
        while True:
            print("Hc send heardbeat to cloud")
            self.__logger.info("Hc send heardbeat to cloud")
            requestTimeCount = datetime.datetime.now().timestamp()
            if self.__cache.DisconnectTime is None:
                self.__cache.DisconnectTime = datetime.datetime.now()
            ok = await s.SendHttpRequestToHeardbeatUrl(self.__httpServices)
            if not ok:
                print("can not ping to cloud")
                if datetime.datetime.now().timestamp() - requestTimeCount > 20:
                    requestTimeCount = 0
                    self.__hcUpdateDisconnectStToDb()
                signalrDisconnectCount = signalrDisconnectCount + 1
                self.__cache.SignalrConnectSuccessFlag = False
                self.__cache.PingCloudSuccessFlag = False
            if ok:
                await s.RecheckReconnectStatusOfLastActiveInDb()
                if not firstPingSuccessToCloudFlag:
                    firstPingSuccessToCloudFlag = True
                self.__cache.PingCloudSuccessFlag = True
                self.__cache.DisconnectTime = None
                signalrDisconnectCount = 0
            await asyncio.sleep(15)
            if (signalrDisconnectCount == 12) and (not self.__cache.SignalrDisconnectStatusUpdateStatusFlag):
                self.__hcUpdateDisconnectStToDb()
                if firstPingSuccessToCloudFlag:
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

    async def __HcHandlerMqttData(self):
        while True:
            await asyncio.sleep(0.1)
            if not self.__mqttServices.mqttDataQueue.empty():
                with self.__lock:
                    item = self.__mqttServices.mqttDataQueue.get()
                    self.__mqttHandler.Handler(item)
                    self.__mqttServices.mqttDataQueue.task_done()

    async def __HcHandlerSignalRData(self):
        while True:
            await asyncio.sleep(0.1)
            if not self.__signalServices.signalrDataQueue.empty():
                with self.__lock:
                    item = self.__signalServices.signalrDataQueue.get()
                    self.__signalrHandler.Handler(item)
                    self.__signalServices.signalrDataQueue.task_done()

    async def __HcCheckAndReconnectSignalrWhenHaveInternet(self):
        while True:
            while not self.__cache.NeedReconnectSignalrServerFlag:
                await asyncio.sleep(2)
            s = System(self.__logger)
            while not s.pingGoogle():
                await asyncio.sleep(2)
            while not self.__cache.PingCloudSuccessFlag:
                await asyncio.sleep(2)
            await self.__signalServices.DisConnect()
            self.__signalServices.ReConnect()
            self.__cache.NeedReconnectSignalrServerFlag = False

    def __HcLoadUserData(self):
        userData = self.__db.Services.UserdataServices.FindUserDataById(id=1)
        dt = userData.first()
        if dt is not None:
            self.__cache.EndUserId = dt["EndUserProfileId"]
            self.__cache.RefreshToken = dt["RefreshToken"]

    async def Run(self):
        self.__HcLoadUserData()
        self.__mqttServices.Init()
        task0 = asyncio.create_task(self.__signalServices.Init())
        task1 = asyncio.create_task(self.__HcHandlerSignalRData())
        task2 = asyncio.create_task(self.__HcCheckConnectWithCloud())
        task3 = asyncio.create_task(self.__HcHandlerMqttData())
        task4 = asyncio.create_task(self.__HcCheckAndReconnectSignalrWhenHaveInternet())
        tasks = [task0, task1, task2, task3, task4]
        await asyncio.gather(*tasks)
