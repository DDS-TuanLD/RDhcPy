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
            if(self.__disconnectRetryCount == 60):
                self.__disconnectRetryCount = 0
                print("Disconnect signalr server timeout")
                self.__logger.error("Disconnect signalr timeout")
                t = datetime.datetime.now().timestamp()-60
                s = System()
                s.EliminateCurrentProgess()
                s.UpdateDisconnectStatusToDb(DisconnectTime=datetime.datetime.fromtimestamp(t))
                
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
        try:
            self.__hub.send("Send", [endUserProfileId, entity , message])
        except Exception as err:
            self.__logger.error(f"Error when send data to cloud: {err}")
       
    async def Init(self):
        while self.__cache.RefreshToken == "":
            await asyncio.sleep(1)
        self.__buildConnection()
        connectSuccess = False
        while connectSuccess == False:
            try:
                self.__hub.start()
                connectSuccess = True
            except Exception as err:
                self.__logger.error(f"Exception when connect with signalr server: {err}")
                print(f"Exception when connect with signalr server: {err}")
                self.__cache.signalrConnectSuccess = False
                await asyncio.sleep(5)
        self.__cache.signalrConnectSuccess = True
        self.__onConnect()
        self.__onDisconnect()
        self.__onReceiveData()
    
    def ReConnect(self):
        try:
            self.__hub.start()
        except Exception as err:
            self.__logger.error(f"Exception when connect with signalr server: {err}")
        
    def Receive(self):
        pass
    
    def HandlerData(self):
        pass