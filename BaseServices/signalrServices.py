import signalrcore.hub_connection_builder as SignalrBuilder
import asyncio
import queue
import os

class MetaSignalServices(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaSignalServices, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
class SignalrServices(metaclass=MetaSignalServices):
    __hub=SignalrBuilder.HubConnectionBuilder
    __queue = queue.Queue()
    
    def ConnectToServer(self):
        self.__hub = SignalrBuilder.HubConnectionBuilder()\
        .with_url(os.getenv("SERVER_TEST"), options={"verify_ssl": False}) \
        .with_automatic_reconnect({
                "type": "interval",
                "keep_alive_interval": 10,
                "intervals": [1, 3, 5, 6, 7, 87, 3]
            }).build()
        return self
    
    def StartServices(self):
        startSuccess = False
        try:
            self.__hub.start()
            startSuccess = True
        except Exception as err:
            print(f"Exception when connect with signalr server: {err}")
        return startSuccess

    def OnReceiveData(self):
       self.__hub.on("ReceiveMessage", lambda data: self.__queue.put_nowait(data))

    def DisConnectWithServer(self):
        self.__hub.stop()

    def SendMesageToServer(
        self, username: str = "RdGateway", mess: str = ""):
        """ This is function support send data to server

        Args:
            username (str, optional): [name of gateway]. Defaults to "RdGateway".
            mess (str, optional): [string need to send]. Defaults to "".
        """
        
        self.__hub.send("SendMessage", [username, mess])
        
    async def OnHandlerReceiveData(self):
        """ function handler receive data
        """
        
        while True:
            await asyncio.sleep(0.5)
            if self.__queue.empty() == False:
                item = self.__queue.get()
                print(str(item))
           