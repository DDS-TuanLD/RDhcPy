import asyncio
from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.sql import select, Select
from sqlalchemy import insert

class users():
    __id: int
    __name: str
    __fullname: str
    
    def __init__(self, userId: int, name: str, fullname: str):
        self.__id = userId
        self.__name = name
        self.__fullname = fullname
        
    @property
    def UserId(self):
        return self.__id
    
    @UserId.setter
    def UserId(self, id: int):
        self.__id = id
        
    @property
    def UserName(self):
        return self.__name
    
    @UserName.setter
    def UserName(self, id: int):
        self.__name = id
        
    @property
    def UserFullName(self):
        return self.__fullname
    
    @UserFullName.setter
    def UserFullName(self, id: int):
        self.__fullname = id
      
class usersTable():
    def __init__(self, metadata: MetaData):
        self.userTable = Table('users', metadata,
                        Column('id', Integer, primary_key=True, nullable=False),
                        Column('name', String),
                        Column('fullname', String),
                        )  