class MetaCache(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaCache, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
    
class HcCache(metaclass=MetaCache):
    __refreshToken: str
    
    def __init__(self):
        self.__refreshToken = ""
        
    @property
    def RefreshToken(self):
        return self.__refreshToken
    
    @RefreshToken.setter
    def RefreshToken(self, refreshToken: str):
        self.__refreshToken = refreshToken
        
    def SaveRefreshToken(self, token :str):
        self.__refreshToken = str
        
