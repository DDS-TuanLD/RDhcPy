class MetaCache(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaCache, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
    
class HcCache(metaclass=MetaCache):
    __refreshToken: str
    __signalrOnConnect: bool
    __signalrDisconnectCount: int
    __signalrDisconnectStatusUpdate: bool
    
    def __init__(self):
        self.__refreshToken = ""
        self.__signalrOnConnect = True
        self.__signalrDisconnectCount = 0
        self.__signalrDisconnectStatusUpdate = False
        
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
           
    def SaveRefreshToken(self, token :str):
        self.__refreshToken = str
        
