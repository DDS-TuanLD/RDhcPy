import asyncio
from sqlalchemy import Column, Integer, String
from sqlalchemy import DateTime
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
import datetime
import time

class userData():
    __id: int
    __refreshToken: str
    __endUserProfileId: str
    
    def __init__(self, refreshToken: str, endUserProfileId: str):
       self.__refreshToken = refreshToken
       self.__endUserProfileId = endUserProfileId
       
    @property
    def RefreshToken(self):
        return self.__refreshToken
    
    @RefreshToken.setter
    def RefreshToken(self, refreshToken: str):
        self.__refreshToken = refreshToken
        
    @property
    def EndUserProfileId(self):
        return self.__endUserProfileId
    
    @EndUserProfileId.setter
    def EndUserProfileId(self, EndUserProfileId: str):
        self.__endUserProfileId = EndUserProfileId