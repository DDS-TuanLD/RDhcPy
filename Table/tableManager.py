from Table.systemConfigurationTable import systemConfigurationTable
from sqlalchemy import MetaData

class MetaTable(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaTable, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class tableManager(metaclass=MetaTable):
    __systemConfigurationTable: systemConfigurationTable
        
    def __init__(self, metadata: MetaData):
        self.__systemConfigurationTable = systemConfigurationTable(metadata)
    
    @property
    def SystemConfigurationTable(self):
        return self.__systemConfigurationTable.systemConfigurationTable
    