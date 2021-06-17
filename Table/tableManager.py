from Table.systemConfigurationTable import systemConfigurationTable
from Table.userDataTable import userDataTable
from sqlalchemy import MetaData
from Table.userDataTable import userDataTable

class MetaTable(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaTable, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class tableManager(metaclass=MetaTable):
    __systemConfigurationTable: systemConfigurationTable
    __userDataTable: userDataTable
        
    def __init__(self, metadata: MetaData):
        self.__systemConfigurationTable = systemConfigurationTable(metadata)
        self.__userDataTable = userDataTable(metadata)
    
    @property
    def SystemConfigurationTable(self):
        return self.__systemConfigurationTable.systemConfigurationTable
    
    @property
    def UserDataTable(self):
        return self.__userDataTable.userDataTable