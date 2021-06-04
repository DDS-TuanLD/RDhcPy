import signalrcore.hub_connection_builder as SignalrBuilder
import asyncio

class SignalrClient():
    
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

    async def SendMesageToServer(self, username="", mess=""):
        if username == "":
            await self.hub.send("Send", [mess])
        else:
            await self.hub.send("Send", [username, mess])
        return self
        
    