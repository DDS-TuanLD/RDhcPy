import asyncio
from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.sql import select, Select
from sqlalchemy import insert
import datetime
import time
class systemConfiguration():
    __id: int
    __isConnect: bool
    __createAt: datetime.datetime
    __updateAt: datetime.datetime
    
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
        
    @property
    def CreateAt(self):
        return self.__createAt
    
    @CreateAt.setter
    def CreateAt(self, CreateAt: datetime.datetime):
        self.__createAt = CreateAt
        
    @property
    def UpdateAt(self):
        return self.__createAt
    
    @UpdateAt.setter
    def UpdateAt(self, CreateAt: datetime.datetime):
        self.__createAt = CreateAt
      
      
class systemConfigurationTable():
    def __init__(self, metadata: MetaData):
        self.systemConfigurationTable = Table('SystemConfiguration', metadata,
                        Column('id', Integer, primary_key=True, nullable=False),
                        Column('IsConnect', String),
                        Column('CreateAt', String),
                        Column('UpdateAt', String),
                        )  