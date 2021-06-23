import datetime
class MetaCache(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaCache, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
    
class HcCache(metaclass=MetaCache):
    __refreshToken: str
    __endUserId: str
    __signalrOnConnect: bool
    __signalrDisconnectCount: int
    __signalrDisconnectStatusUpdate: bool
    __disconectTime: datetime.datetime
 
    def __init__(self):
        self.__refreshToken = "10a8F5yStJ1A7JBXRzc4NdO67kxbZtbxGYQPyOFlQXiRR/nI9ZrTzAwCUYrq2DUnFt915wjAkXoGjGsIoL814I7fO5swdgc2xd6AV6WPwF8Bum0fEXbv9mV13A2Y0aJ/89pw1KFTtmX3UVLZOyrixUVRmEwxQEPSsFORFQOV8NGEcOXrxQPz6gjyFl1JpDz9ZsFrgFLouyitefqX6srCsA2WH5ztuXnULKkw8XtGxL8="
        self.__signalrOnConnect = True
        self.__signalrDisconnectCount = 0
        self.__signalrDisconnectStatusUpdate = False
        self.__endUserId = "10033"
        self.__disconectTime = None
        self.mqttDisconnectStatus = False
        self.mqttProblemCount = 0
    @property
    def RefreshToken(self):
        return self.__refreshToken
    
    @RefreshToken.setter
    def RefreshToken(self, refreshToken: str):
        self.__refreshToken = refreshToken
    
    @property
    def SignalrConnectStatus(self):
        return self.__signalrOnConnect
    
    @SignalrConnectStatus.setter
    def SignalrConnectStatus(self, onConnect: bool):
        self.__signalrOnConnect = onConnect
        
    @property
    def SignalrDisconnectCount(self):
        return self.__signalrDisconnectCount
    
    @SignalrDisconnectCount.setter
    def SignalrDisconnectCount(self, count: int):
        self.__signalrDisconnectCount = count
        
    @property
    def SignalrDisconnectStatusUpdate(self):
        return self.__signalrDisconnectStatusUpdate
    
    @SignalrDisconnectStatusUpdate.setter
    def SignalrDisconnectStatusUpdate(self, updateStatus: bool):
        self.__signalrDisconnectStatusUpdate = updateStatus
           
    @property
    def EndUserId(self):
        return self.__endUserId
    
    @EndUserId.setter
    def EndUserId(self, EndUserId: str):
        self.__endUserId = EndUserId
        
    @property
    def Token(self):
        return self.__token
    
    @EndUserId.setter
    def Token(self, token: str):
        self.__token = token
        
          
    @property
    def DisconnectTime(self):
        return self.__disconectTime
    
    @DisconnectTime.setter
    def DisconnectTime(self, disconnectTime: datetime.datetime):
        self.__disconectTime = disconnectTime