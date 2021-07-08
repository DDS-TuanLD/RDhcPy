import datetime
class MetaCache(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaCache, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
    
class Cache(metaclass=MetaCache):
    __refreshToken: str
    __endUserId: str
    __signalrDisconnectCount: int
    __signalrDisconnectStatusUpdate: bool
    __disconectTime: datetime.datetime
    __recheckConnectionStatusInDb: bool
    __resetSignalrConnect: bool
    __signalrConnectSuccess: bool
    __pingCloudSuccess: bool
    __firstPingSuccessToCloud: bool
    
    def __init__(self):
        self.__signalrConnectSuccess = False
        self.__refreshToken = ""
        self.__signalrDisconnectCount = 0
        self.__signalrDisconnectStatusUpdate = False
        self.__endUserId = ""
        self.__disconectTime = None
        self.__recheckConnectionStatusInDb = False
        self.__resetSignalrConnect = False
        self.__pingCloudSuccess = None
        self.__firstPingSuccessToCloud = False

    @property
    def FirstPingSuccessToCloudFlag(self):
        return self.__firstPingSuccessToCloud
    
    @FirstPingSuccessToCloudFlag.setter
    def FirstPingSuccessToCloudFlag(self, firstPingSuccessToCloud: bool):
        self.__firstPingSuccessToCloud = firstPingSuccessToCloud
    
    @property    
    def PingCloudSuccessFlag(self):
        return self.__pingCloudSuccess

    @PingCloudSuccessFlag.setter
    def PingCloudSuccessFlag(self, pingCloudSuccess: bool):
        self.__pingCloudSuccess = pingCloudSuccess
    
    
    @property
    def SignalrConnectSuccessFlag(self):
        return self.__signalrConnectSuccess
    
    @SignalrConnectSuccessFlag.setter
    def SignalrConnectSuccessFlag(self, signalrConnectSuccess: bool):
        self.__signalrConnectSuccess = signalrConnectSuccess
      
    @property
    def ResetSignalrConnectFlag(self):
        return self.__resetSignalrConnect
    
    @ResetSignalrConnectFlag.setter
    def ResetSignalrConnectFlag(self, resetSignalrConnect: bool):
        self.__resetSignalrConnect = resetSignalrConnect
        
    @property
    def RecheckConnectionStatusInDbFlag(self):
        return self.__recheckConnectionStatusInDb
    
    @RecheckConnectionStatusInDbFlag.setter
    def RecheckConnectionStatusInDbFlag(self, recheckConnectionStatusInDb: bool):
        self.__recheckConnectionStatusInDb = recheckConnectionStatusInDb
    
    @property
    def RefreshToken(self):
        return self.__refreshToken
    
    @RefreshToken.setter
    def RefreshToken(self, refreshToken: str):
        self.__refreshToken = refreshToken
            
    @property
    def SignalrDisconnectCount(self):
        return self.__signalrDisconnectCount
    
    @SignalrDisconnectCount.setter
    def SignalrDisconnectCount(self, signalrDisconnectCount: int):
        self.__signalrDisconnectCount = signalrDisconnectCount
        
    @property
    def SignalrDisconnectStatusUpdateStatusFlag(self):
        return self.__signalrDisconnectStatusUpdate
    
    @SignalrDisconnectStatusUpdateStatusFlag.setter
    def SignalrDisconnectStatusUpdateStatusFlag(self, signalrDisconnectStatusUpdate: bool):
        self.__signalrDisconnectStatusUpdate = signalrDisconnectStatusUpdate
           
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