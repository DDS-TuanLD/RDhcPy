import signalrcore.hub_connection_builder as SignalrBuilder
from Contract.ISignalrServices import ISignalrBaseServices
import asyncio

class SignalrClient(ISignalrBaseServices):
    
    def __init__(self):
        self.hub = SignalrBuilder.HubConnectionBuilder().build()
    
    def StartConnectToServer(self):
        self.hub.start()
        return self

    def DisConnectWithServer(self):
        self.hub.stop()

    def ListenOnEvent(self, event, call_back: callable):
        self.hub.on(event, call_back)
        return self

    async def SendMesageToServer(self, username, mess):
        await self.hub.send("Send", [username, mess])
        return self
        
    