import signalrcore.hub_connection_builder as SignalrBuilder
import asyncio
import queue
import requests
from Cache.HcCache import HcCache
import Constant.constant as const
import logging
import threading

def getToken():
    cache = HcCache()
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
  
class SignalrServices():
    __hub: SignalrBuilder.HubConnectionBuilder
    signalrDataQueue: queue.Queue
    __cache: HcCache
    __logger: logging.Logger
    __lock: threading.Lock
    
    def __init__(self, log: logging.Logger):
        self.__logger = log
        self.__cache = HcCache()
        self.__lock = threading.Lock()
        self.signalrDataQueue = queue.Queue()
        
    def BuildConnection(self):
        self.__hub = SignalrBuilder.HubConnectionBuilder()\
        .with_url(const.SERVER_HOST + const.SIGNALR_SERVER_URL, 
                options={
                        "access_token_factory": getToken,
                        "headers": {
                        }
                    }) \
        .build()
        return self
    
    async def StartConnect(self):
        startSuccess = False
        while startSuccess == False:
            try:
                self.__hub.start()
                startSuccess = True
            except Exception as err:
                self.__logger.error(f"Exception when connect with signalr server: {err}")
                await asyncio.sleep(5)
                
    def Startconnect(self):
        try:
            self.__hub.start()
            startSuccess = True
        except Exception as err:
            self.__logger.error(f"Exception when connect with signalr server: {err}")
            
    def OnReceiveData(self):
        self.__hub.on("Receive", self.__dataPreHandler)
    
    def __dataPreHandler(self, data):
        with self.__lock:
            self.signalrDataQueue.put(data)
        
    def DisConnectWithServer(self):
        try:
            self.__hub.stop()
        except:
            pass
        
    async def Disconnect(self):
        startSuccess = False
        while startSuccess == False:
            try:
                self.__hub.stop()
                startSuccess = True
            except Exception as err:
                self.__logger.error(f"Exception when disconnect with signalr server: {err}")
                await asyncio.sleep(5)

    def SendMesageToServer(
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
       
   
