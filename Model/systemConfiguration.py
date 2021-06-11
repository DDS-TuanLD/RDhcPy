import asyncio
from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine, DateTime, func
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.sql import select, Select
from sqlalchemy import insert, Boolean
import datetime
import time
class systemConfiguration():
    __id: int
    __isConnect: bool
    
    def __init__(self, isConnect: bool):
        self.__isConnect = isConnect
        
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
class systemConfigurationTable():
    def __init__(self, metadata: MetaData):
        self.systemConfigurationTable = Table('SystemConfiguration', metadata,
                        Column('id', Integer, primary_key=True, nullable=False),
                        Column('IsConnect', String),
                        Column('CreateAt', DateTime, server_default = func.now()),
                        )  