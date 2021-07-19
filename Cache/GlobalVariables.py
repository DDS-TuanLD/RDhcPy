import datetime
class MetaGlobalVariables(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaGlobalVariables, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class GlobalVariables(metaclass=MetaGlobalVariables):
    __refreshToken: str
    __endUserId: str
    __signalrDisconnectStatusUpdate: bool
    __disconectTime: datetime.datetime
    __recheckConnectionStatusInDb: bool
    __resetSignalrConnect: bool
    __signalrConnectSuccess: bool
    __pingCloudSuccess: bool

    def __init__(self):
        self.__signalrConnectSuccess = False
        self.__refreshToken = ""
        self.__signalrDisconnectStatusUpdate = False
        self.__endUserId = ""
        self.__disconectTime = None
        self.__recheckConnectionStatusInDb = False
        self.__resetSignalrConnect = False
        self.__pingCloudSuccess = None

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