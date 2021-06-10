from Model.systemConfiguration import systemConfigurationTable, systemConfiguration
from databases import Database

class systemConfigurationRepo():
    __systemConfigurationTable: systemConfigurationTable
    __context: Database
    
    def __init__(self, SystemConfigurationTable: systemConfigurationTable, context: Database):
        self.__systemConfigurationTable = SystemConfigurationTable
        self.__context = context
    
    def Create(self):
        pass

    def Remove(self):
        pass

    def Update(self):
        pass

    def Delete(self):
        pass
    
    def FindAll(self):
        pass
    
    def FindWithCOndition(self):
        pass