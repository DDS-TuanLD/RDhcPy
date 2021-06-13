from Repository.systemConfigurationRepo import systemConfigurationRepo
from Model.systemConfiguration import systemConfiguration
from sqlalchemy import Table
from sqlalchemy.engine.base import Connection

class systemConfigurationServices():
    __systemConfigurationRepo: systemConfigurationRepo
    
    def __init__(self, SystemConfigurationTable: Table, context: Connection):
        self.__systemConfigurationRepo = systemConfigurationRepo(SystemConfigurationTable=SystemConfigurationTable, context=context)
        
    def AddNewSysConfiguration(self, sysConfig: systemConfiguration):
        self.__systemConfigurationRepo.CreateWithParams(sysConfig)