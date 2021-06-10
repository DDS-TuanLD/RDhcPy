from Cache.HcCache import HcCache
class DataHandlerService():  
    def MqttDataHandler(self, args):
        pass
    
    def SignalrDataHandler(self, *args):
        switcher = {
            "Heardbeat": self.HeardbeatHandler
        }
        func = switcher.get(args[0][0])
        func(args[0][1])
    
    def HeardbeatHandler(self, data: str=""):
        cache = HcCache()
        if data == "pong":
            cache.SignalrDisconnectCount = 0
            cache.SignalrConnectStatus = True
            cache.SignalrDisconnectStatusUpdate = False
            print(data)
            
        
    