import signalrcore.hub_connection_builder as SignalrBuilder
import asyncio
import queue
import requests
from Cache.Cache import Cache
import Constant.constant as const
import logging
import threading
from Contracts.Itransport import Itransport
import time
from Helper.System import System
import datetime

def getToken():
    cache = Cache()
    try:
        renew_token = "https://iot-dev.truesight.asia/rpc/iot-ebe/account/renew-token"
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        headers['X-EndUserProfileId'] = cache.EndUserId
        headers['Cookie'] = "RefreshToken={refresh_token}".format(refresh_token=cache.RefreshToken)
        response = requests.post(renew_token, json=None, headers=headers).json()
        token = response['token']
        headers['Cookie'] = "Token={token}".format(token=token)
        return token
    except Exception as e:
        return None
  
class Signalr(Itransport):
    __hub: SignalrBuilder.HubConnectionBuilder
    signalrDataQueue: queue.Queue
    __cache: Cache
    __logger: logging.Logger
    __lock: threading.Lock
    __disconnectFlag: int
    __disconnectRetryCount: int
    
    def __init__(self, log: logging.Logger):
        self.__logger = log
        self.__cache = Cache()
        self.__lock = threading.Lock()
        self.signalrDataQueue = queue.Queue()
        self.__disconnectFlag = 1
        self.__disconnectRetryCount = 0
        
    def __buildConnection(self):
        self.__hub = SignalrBuilder.HubConnectionBuilder()\
        .with_url(const.SERVER_HOST + const.SIGNALR_SERVER_URL, 
                options={
                        "access_token_factory": getToken,
                        "headers": {
                        }
                    }) \
        .with_automatic_reconnect({
                "type": "raw",
                "keep_alive_interval": 5,
                "reconnect_interval": 5,
                "max_attempts": 50
                })\
        .build()
        return self
    
    def __onReceiveData(self):
        self.__hub.on("Receive", self.__dataPreHandler)
      
    def __onDisconnect(self):
        self.__hub.on_close(self.__disconnect)
    
    def __disconnect(self):
        print("disconnect to signalr server")
        self.__disconnectFlag = 0
        self.__disconnectRetryCount = 0
    
    def __onConnect(self):
        self.__hub.on_open(lambda: print("Connect to signalr server"))
        
    def __dataPreHandler(self, data):
        with self.__lock:
            self.signalrDataQueue.put(data)
        
    async def DisConnect(self):
        self.__disconnectFlag = 1
        try:
            self.__hub.stop()
        except Exception as err:
            self.__logger.error(f"Exception when disconnect with signalr server: {err}")
        await asyncio.sleep(1)
        if self.__disconnectFlag == 1:
            if(self.__disconnectRetryCount == 30):
                self.__disconnectRetryCount = 0
                print("Disconnect signalr server timeout")
                self.__logger.error("Disconnect signalr timeout")
                t = datetime.datetime.now().timestamp()-30
                s = System(self.__logger)
                s.UpdateDisconnectStatusToDb(DisconnectTime=datetime.datetime.fromtimestamp(t))
                s.EliminateCurrentProgess()

            self.__disconnectRetryCount = self.__disconnectRetryCount + 1
            print(f"Retry to disconnect signalr server {self.__disconnectRetryCount} times")
            await self.DisConnect()

            
    def Send(
        self, endUserProfileId: str = "", entity: str="", message: str=""):
        """ This is function support send data to server

        Args:
            username (str, optional): [name of gateway]. Defaults to "RdGateway".
            mess (str, optional): [string need to send]. Defaults to "".
        """
        self.__hub.send("Send", [endUserProfileId, entity , message])
       
    async def Init(self):
        runOnlyOne = False
        while self.__cache.RefreshToken == "":
            await asyncio.sleep(1)
        self.__buildConnection()
        self.__onConnect()
        self.__onDisconnect()
        self.__onReceiveData()
        while True:
            try:
                if self.__cache.SignalrConnectSuccessFlag == False and runOnlyOne == False:
                    self.__hub.start()
                    self.__cache.SignalrConnectSuccessFlag = True
                    runOnlyOne = True
                    
                if self.__cache.ResetSignalrConnectFlag == True:
                    await self.DisConnect()
                    self.ReConnect()
                    self.__cache.ResetSignalrConnectFlag = False    
            except Exception as err:
                self.__logger.error(f"Exception when connect with signalr server: {err}")
                print(f"Exception when connect with signalr server: {err}")
                self.__cache.SignalrConnectSuccessFlag = False
            await asyncio.sleep(3)
       
    def ReConnect(self):
        try:
            self.__hub.start()
        except Exception as err:
            self.__logger.error(f"Exception when connect with signalr server: {err}")
        
    def Receive(self):
        pass
    
    def HandlerData(self):
        pass