from Repository.systemConfigurationRepo import systemConfigurationRepo
from Model.systemConfiguration import systemConfiguration
from sqlalchemy import Table
from sqlalchemy.engine.base import Connection


class MetaSystemConfigurationServices(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaSystemConfigurationServices, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
class systemConfigurationServices(metaclass=MetaSystemConfigurationServices):
    __systemConfigurationRepo: systemConfigurationRepo
    
    def __init__(self, SystemConfigurationTable: Table, context: Connection):
        self.__systemConfigurationRepo = systemConfigurationRepo(SystemConfigurationTable=SystemConfigurationTable, context=context)
        
    def AddNewSysConfiguration(self, sysConfig: systemConfiguration):
        self.__systemConfigurationRepo.CreateWithParams(sysConfig)
        
    def FindSysConfigurationById(self, id:int):
        rel = self.__systemConfigurationRepo.FindwithId(id)
        return rel
    