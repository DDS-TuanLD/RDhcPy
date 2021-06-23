import asyncio
from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.sql import select, Select
from sqlalchemy import insert
from sqlalchemy.engine.base import Connection
import Constant.constant as const
from Table.tableManager import tableManager
from ModelServices.modelServicesManager import modelServicesManager

# class MetaDb(type):
#     _instances = {}
#     def __call__(cls, *args, **kwargs):
#         if cls not in cls._instances:
#             cls._instances[cls] = super(MetaDb, cls).__call__(*args, **kwargs)
#         return cls._instances[cls]
    
class Db():
    __metadata = MetaData()
    __engine: create_engine
    __connect: Connection    
    __dbTable: tableManager
    __servicesManager: modelServicesManager
    
    def Init(self, dbName: str):
        self.__createTable(dbName)
        self.__createContext()
        self.__servicesInit()
       
    def __createTable(self, dbName: str):
        self.__engine = create_engine('sqlite:///' + dbName, echo=True)
        self.__dbTable = tableManager(self.__metadata)
        self.__metadata.create_all(self.__engine)
        
    def __createContext(self):
        self.__connect = self.__engine.connect() 
        
    def __servicesInit(self):
        self.__servicesManager = modelServicesManager(self.__dbTable, self.__connect)

    @property
    def Table(self):
        return self.__dbTable
    
    @property
    def Services(self):
        return self.__servicesManager