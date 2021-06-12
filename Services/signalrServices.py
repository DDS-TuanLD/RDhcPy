import signalrcore.hub_connection_builder as SignalrBuilder
import asyncio
import queue
import requests
from Cache.HcCache import HcCache
from Handler.dataHandler import DataHandlerService
import Constant.constant as const

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
    __hub=SignalrBuilder.HubConnectionBuilder
    __queue = queue.Queue()
    
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
    
    def StartConnect(self):
        try:
            self.__hub.start()
        except Exception as err:
            print(f"Exception when start signal server {err}")

    def OnReceiveData(self):
       self.__hub.on("Receive", lambda data: self.__queue.put_nowait(data))

    def DisConnectWithServer(self):
        self.__hub.stop()

    def SendMesageToServer(
        self, endUserProfileId: str ="", entity: str="", message: str=""):
        """ This is function support send data to server

        Args:
            username (str, optional): [name of gateway]. Defaults to "RdGateway".
            mess (str, optional): [string need to send]. Defaults to "".
        """
        self.__hub.send("Send", ["10033", entity , message])
    
    async def SignalrServicesInit(self):
        startSuccess = False
        while startSuccess == False:
            try:
                self.BuildConnection()
                self.__hub.start()
                startSuccess = True
            except Exception as err:
                print(f"Exception when connect with signalr server: {err}")
                await asyncio.sleep(5)
        self.OnReceiveData()

    async def OnHandlerReceiveData(self):
        """ function handler receive data
        """
        
        hander = DataHandlerService()
        while True:
            await asyncio.sleep(0.5)
            if self.__queue.empty() == False:
                item = self.__queue.get()
                await hander.SignalrDataHandler(item)
           