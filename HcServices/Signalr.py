import signalrcore.hub_connection_builder as SignalrBuilder
import asyncio
import queue
import requests
from Cache.Cache import Cache
import Constant.constant as const
import logging
import threading
from Contracts.Itransport import Itransport

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
    
    def __init__(self, log: logging.Logger):
        self.__logger = log
        self.__cache = Cache()
        self.__lock = threading.Lock()
        self.signalrDataQueue = queue.Queue()
        
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
    
    async def __startConnect(self):
        startSuccess = False
        while startSuccess == False:
            try:
                self.__hub.start()
                startSuccess = True
            except Exception as err:
                self.__logger.error(f"Exception when connect with signalr server: {err}")
                await asyncio.sleep(5)
        self.__onReceiveData()

    def __onReceiveData(self):
        self.__hub.on("Receive", self.__dataPreHandler)
      
    
    def __dataPreHandler(self, data):
        with self.__lock:
            self.signalrDataQueue.put(data)
        
    def DisConnect(self):
        try:
            self.__hub.stop()
        except Exception as err:
            self.__logger.error(f"Exception when disconnect with signalr server: {err}")

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
        self.__buildConnection();
        while self.__cache.RefreshToken == "":
            await asyncio.sleep(1)
        await self.__startConnect()
            
    def ReConnect(self):
        try:
            self.__hub.start()
        except Exception as err:
            self.__logger.error(f"Exception when connect with signalr server: {err}")
        self.__onReceiveData()
        
    def Receive(self):
        pass
    
    def HandlerData(self, data):
        pass
        