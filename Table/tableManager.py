from Table.systemConfigurationTable import systemConfigurationTable
from Table.userDataTable import userDataTable
from sqlalchemy import MetaData
from Table.userDataTable import userDataTable

class tableManager():
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