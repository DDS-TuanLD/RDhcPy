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
    signalrConnectSuccess: bool
    pingCloudHttp: bool
    __recheckConnectionStatusInDb: bool
    # __firstPullDataToCloud: bool
    
    def __init__(self):
        self.pingCloudHttp = None
        self.signalrConnectSuccess = None
        self.__refreshToken = ""
        self.__signalrDisconnectCount = 0
        self.__signalrDisconnectStatusUpdate = False
        self.__endUserId = ""
        self.__disconectTime = None
        self.mqttDisconnectStatus = False
        self.mqttProblemCount = 0
        self.__recheckConnectionStatusInDb = False
        # self.__firstPullDataToCloud = False
      
    # @property
    # def FirstPullDataToCloud(self):
    #     return self.__firstPullDataToCloud
    
    # @FirstPullDataToCloud.setter
    # def FirstPullDataToCloud(self, firstPull: bool):
    #     self.__firstPullDataToCloud = firstPull 
        
    @property
    def RecheckConnectionStatusInDb(self):
        return self.__recheckConnectionStatusInDb
    
    @RecheckConnectionStatusInDb.setter
    def RecheckConnectionStatusInDb(self, recheckStatus: bool):
        self.__recheckConnectionStatusInDb = recheckStatus
    
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