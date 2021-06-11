from Cache.HcCache import HcCache
from Database.Db import Db
from Model.systemConfiguration import systemConfiguration
import datetime
class DataHandlerService():  
    def MqttDataHandler(self, args):
        pass
    
    async def SignalrDataHandler(self, *args):
        switcher = {
            "Heardbeat": self.HeardbeatHandler
        }
        func = switcher.get(args[0][0])
        await func(args[0][1])
    
    async def HeardbeatHandler(self, data: str=""):
        cache = HcCache()
        db = Db()
        if data == "pong":
            cache.SignalrDisconnectCount = 0
            if cache.SignalrDisconnectStatusUpdate == True:
                print("Update cloud reconnect status to db")
                await db.DbSystemConfigurationRepo.CreateWithParamsAsync(IsConnect=True, DisconnectTime=None, ReconnectTime=datetime.datetime.now())
                cache.SignalrDisconnectStatusUpdate = False
                cache.DisconnectTime = None
            
        
    