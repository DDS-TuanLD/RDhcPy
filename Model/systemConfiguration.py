import asyncio
from sqlalchemy import Column, Integer, String
from sqlalchemy import DateTime
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
import datetime
import time
class systemConfiguration():
    __id: int
    __isConnect: bool
    __disconnectTime: datetime.datetime
    __reconnectTime: datetime.datetime
    
    def __init__(self, isConnect: bool, DisconnectTime: datetime.datetime, ReconnectTime: datetime.datetime):
        self.__isConnect = isConnect
        self.__disconnectTime = DisconnectTime
        self.__reconnectTime = ReconnectTime
        
    @property
    def Id(self):
        return self.__id
    
    @Id.setter
    def Id(self, id: int):
        self.__id = id
        
    @property
    def IsConnect(self):
        return self.__isConnect
    
    @IsConnect.setter
    def IsConnect(self, IsConnect: bool):
        self.__isConnect = IsConnect
    
    @property
    def DisconnectTime(self):
        return self.__disconnectTime
    
    @DisconnectTime.setter
    def DisconnectTime(self, DisconnectTime: bool):
        self.__disconnectTime = DisconnectTime
    
    @property
    def ReconnectTime(self):
        return self.__reconnectTime
    
    @ReconnectTime.setter
    def ReconnectTime(self, ReconnectTime: bool):
        self.__reconnectTime = ReconnectTime
        
