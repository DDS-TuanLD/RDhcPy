import asyncio
from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.sql import select, Select
from sqlalchemy import insert
from Model.systemConfiguration import systemConfigurationTable
from Repository.systemConfigurationRepo import systemConfigurationRepo
from sqlalchemy.engine.base import Connection
import Constant.constant as const
class MetaDb(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaDb, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Db(metaclass= MetaDb):
    __metadata = MetaData()
    __engine: create_engine
    __connect: Connection
    
    __systemConfigurationTable: systemConfigurationTable
    
    __systemConfigurationRepo: systemConfigurationRepo

    def createTable(self):
        self.__engine = create_engine('sqlite:///' + const.DB_NAME, echo=True)
        self.__systemConfigurationTable = systemConfigurationTable(self.__metadata)
        self.__metadata.create_all(self.__engine)
        self.__connect = self.__engine.connect()
        
        
    def DbRepoUpdate(self):
        self.__systemConfigurationRepo = systemConfigurationRepo(self.__systemConfigurationTable.systemConfigurationTable, self.__connect)
    
    @property
    def DbContext(self):
        return self.__connect
    
  
    @property
    def DbSystemConfigurationTable(self):
        return self.__systemConfigurationTable.systemConfigurationTable
    
    @property
    def DbSystemConfigurationRepo(self):
        return self.__systemConfigurationRepo