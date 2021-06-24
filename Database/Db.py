import asyncio
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy.engine.base import Connection
import Constant.constant as const
from Table.tableManager import tableManager
from ModelServices.modelServicesManager import modelServicesManager
  
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