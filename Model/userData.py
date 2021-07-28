class userData:
    __id: int
    __refreshToken: str
    _dormitoryId: str

    def __init__(self, refreshToken: str, dormitoryId: str):
        self.__refreshToken = refreshToken
        self._dormitoryId = dormitoryId

    @property
    def RefreshToken(self):
        return self.__refreshToken

    @RefreshToken.setter
    def RefreshToken(self, refreshToken: str):
        self.__refreshToken = refreshToken

    @property
    def DormitoryId(self):
        return self._dormitoryId

    @DormitoryId.setter
    def DormitoryId(self, DormitoryId: str):
        self._dormitoryId = DormitoryId
