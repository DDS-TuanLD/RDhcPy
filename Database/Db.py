import asyncio
from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.sql import select, Select
from sqlalchemy import insert
from Model.users import usersTable
from Model.systemConfiguration import systemConfigurationTable
from databases import Database
import os
class MetaDb(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaDb, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Db(metaclass= MetaDb):
    __metadata = MetaData()
    __engine: create_engine
    __database: Database
    __usersTable: usersTable
    __systemConfiguration: systemConfigurationTable

    def createTable(self):
        self.__engine = create_engine('sqlite:///' + os.getenv("DB_NAME"), echo=True)
        self.__usersTable = usersTable(self.__metadata)
        self.__systemConfiguration = systemConfigurationTable(self.__metadata)
        self.__metadata.create_all( self.__engine)
    
    async def DbConnect(self):
        self.__database = Database('sqlite:///' + os.getenv("DB_NAME"))
        await self.__database.connect()
    
    @property
    def DbContext(self):
        return self.__database
    
    @property
    def DbUserTable(self):
        return self.__usersTable.userTable
    
    @property
    def DbUserTable(self):
        return self.__systemConfiguration.systemConfigurationTable
    
 