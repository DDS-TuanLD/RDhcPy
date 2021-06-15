import signalrcore.hub_connection_builder as SignalrBuilder
import asyncio
import queue
import requests
from Cache.HcCache import HcCache
import Constant.constant as const
from Model.systemConfiguration import systemConfiguration
from Adapter.dataAdapter import dataAdapter
from Database.Db import Db
import datetime
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

class MetaSignalServices(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaSignalServices, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
    
class SignalrServices():
    __hub=SignalrBuilder.HubConnectionBuilder
    signalrDataQueue = queue.Queue()
    __cache = HcCache()
    __db = Db()
      
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
        self.__hub.on("Receive", lambda data: self.signalrDataQueue.put_nowait(data))
    
        
    def DisConnectWithServer(self):
        self.__hub.stop()

    def SendMesageToServer(
        self, endUserProfileId: str = "", entity: str="", message: str=""):
        """ This is function support send data to server

        Args:
            username (str, optional): [name of gateway]. Defaults to "RdGateway".
            mess (str, optional): [string need to send]. Defaults to "".
        """
        self.__hub.send("Send", [endUserProfileId, entity , message])
    
    async def SignalrServicesInit(self):
        startSuccess = False
        self.BuildConnection()
        while startSuccess == False:
            try:
                self.__hub.start()
                startSuccess = True
            except Exception as err:
                print(f"Exception when connect with signalr server: {err}")
                await asyncio.sleep(5)
        self.OnReceiveData()

   
