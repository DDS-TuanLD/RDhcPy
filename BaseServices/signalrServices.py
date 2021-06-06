import signalrcore.hub_connection_builder as SignalrBuilder
import asyncio
import queue
import os
class SignalrServices():
    __hub=SignalrBuilder.HubConnectionBuilder
    __queue = queue.Queue()
    def ConnectToServer(self):
        try:
            self.__hub = SignalrBuilder.HubConnectionBuilder()\
            .with_url(os.getenv("SIGNALR_SERVER_URL"), options={"verify_ssl": False}) \
            .with_automatic_reconnect({
                    "type": "interval",
                    "keep_alive_interval": 10,
                    "intervals": [1, 3, 5, 6, 7, 87, 3]
                }).build()
        except Exception as err:
            print(f"Exception when connect with signalr server: {err}")
        return self
    
    def Start(self):
        self.__hub.start()

    def OnReceiveData(self):
       self.__hub.on("ReceiveMessage", lambda data: self.__queue.put_nowait(data))

    def DisConnectWithServer(self):
        self.__hub.stop()

    def SendMesageToServer(self, username="RdHcDefault", mess=""):
        self.__hub.send("SendMessage", [username, mess])
        
    async def OnHandlerReceiveData(self):
        while True:
            await asyncio.sleep(0.5)
            if self.__queue.empty() == False:
                item = self.__queue.get()
                print(str(item))
           