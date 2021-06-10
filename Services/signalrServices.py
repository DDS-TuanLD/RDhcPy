import signalrcore.hub_connection_builder as SignalrBuilder
import asyncio
import queue
import os

def get_token():
    return 
class MetaSignalServices(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaSignalServices, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
    
class SignalrServices(metaclass=MetaSignalServices):
    __hub=SignalrBuilder.HubConnectionBuilder
    __queue = queue.Queue()
    
    def BuildConnection(self):
        self.__hub = SignalrBuilder.HubConnectionBuilder()\
        .with_url(os.getenv("SERVER_HOST") + os.getenv("SIGNALR_SERVER_URL"), 
                options={
                        "access_token_factory": get_token,
                        "headers": {
                        }
                    }) \
        .build()
        return self
    
    def StartConnect(self):
        try:
            self.__hub.start()
        except Exception as err:
            pass

    def OnReceiveData(self):
       self.__hub.on("ReceiveMessage", lambda data: self.__queue.put_nowait(data))

    def DisConnectWithServer(self):
        self.__hub.stop()

    def SendMesageToServer(
        self, endUserProfileId: str ="10039", entity: str = "device", message: str = ""):
        """ This is function support send data to server

        Args:
            username (str, optional): [name of gateway]. Defaults to "RdGateway".
            mess (str, optional): [string need to send]. Defaults to "".
        """
        self.__hub.send("Send", [endUserProfileId, entity , message])
    
    async def SignalrServicesInit(self):
        self.BuildConnection()
        startSuccess = False
        while startSuccess == False:
            await asyncio.sleep(5)
            try:
                self.__hub.start()
                startSuccess = True
            except Exception as err:
                print(f"Exception when connect with signalr server: {err}")
        self.OnReceiveData()

    async def OnHandlerReceiveData(self):
        """ function handler receive data
        """
        
        while True:
            await asyncio.sleep(0.5)
            if self.__queue.empty() == False:
                item = self.__queue.get()
                print(str(item))
           