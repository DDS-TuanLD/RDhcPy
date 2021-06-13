from ModelServices.systemConfigurationServices import systemConfigurationServices
from Table.tableManager import tableManager
from sqlalchemy.engine.base import Connection

class MetaService(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaService, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class  modelServicesManager(metaclass=MetaService):
    __systemConfigurationServices: systemConfigurationServices
    
    def __init__(self, table: tableManager, context: Connection):
        self.__systemConfigurationServices = systemConfigurationServices(table.SystemConfigurationTable, context)
    
    @property
    def SystemConfigurationServices(self):
        return self.__systemConfigurationServices