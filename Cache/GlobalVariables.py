import datetime


class MetaGlobalVariables(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaGlobalVariables, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class GlobalVariables(metaclass=MetaGlobalVariables):
    __refreshToken: str
    __dormitoryId: str
    __signalrDisconnectStatusUpdate: bool
    __disconnectTime: datetime.datetime
    __recheckConnectionStatusInDb: bool
    __signalrConnectSuccess: bool
    __pingCloudSuccess: bool
    __pingGoogleStatus: bool
    __allowChangeCloudAccount: bool
    __currentWifiName: str
    __gatewayMac: str

    def __init__(self):
        self.__signalrConnectSuccess = False
        self.__refreshToken = ""
        self.__signalrDisconnectStatusUpdate = False
        self.__dormitoryId = ""
        self.__disconnectTime = None
        self.__recheckConnectionStatusInDb = False
        self.__pingCloudSuccess = None
        self.__pingGoogleStatus = False
        self.__allowChangeCloudAccount = False
        self.__currentWifiName = ""
        self.__gatewayMac = ""

    @property
    def GatewayMac(self):
        return self.__gatewayMac

    @GatewayMac.setter
    def GatewayMac(self, mac: str):
        self.__gatewayMac = mac

    @property
    def PingGoogleSuccessFlag(self):
        return self.__pingGoogleStatus

    @PingGoogleSuccessFlag.setter
    def PingGoogleSuccessFlag(self, pingGoogleStatus: bool):
        self.__pingGoogleStatus = pingGoogleStatus

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
    def SignalrDisconnectStatusUpdateFlag(self):
        return self.__signalrDisconnectStatusUpdate

    @SignalrDisconnectStatusUpdateFlag.setter
    def SignalrDisconnectStatusUpdateFlag(self, signalrDisconnectStatusUpdate: bool):
        self.__signalrDisconnectStatusUpdate = signalrDisconnectStatusUpdate

    @property
    def DormitoryId(self):
        return self.__dormitoryId

    @DormitoryId.setter
    def DormitoryId(self, DormitoryId: str):
        self.__dormitoryId = DormitoryId

    @property
    def DisconnectTime(self):
        return self.__disconnectTime

    @DisconnectTime.setter
    def DisconnectTime(self, disconnectTime: datetime.datetime):
        self.__disconnectTime = disconnectTime

    @property
    def AllowChangeCloudAccountFlag(self):
        return self.__allowChangeCloudAccount

    @AllowChangeCloudAccountFlag.setter
    def AllowChangeCloudAccountFlag(self, allowChangeCloudAccount: bool):
        self.__allowChangeCloudAccount = allowChangeCloudAccount

    @property
    def CurrentWifiName(self):
        return self.__currentWifiName

    @CurrentWifiName.setter
    def CurrentWifiName(self, currentWifiName: str):
        self.__currentWifiName = currentWifiName
