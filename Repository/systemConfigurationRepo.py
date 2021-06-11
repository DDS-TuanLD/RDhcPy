from Model.systemConfiguration import systemConfigurationTable, systemConfiguration
from databases import Database
from sqlalchemy.orm import base
from sqlalchemy import Table
import datetime
class systemConfigurationRepo():
    __systemConfigurationTable: systemConfigurationTable
    __context: Database
    
    def __init__(self, SystemConfigurationTable: Table, context: Database):
        self.__systemConfigurationTable = SystemConfigurationTable
        self.__context = context
    
    async def Create(self, SystemConfiguration: systemConfiguration):
        ins = self.__systemConfigurationTable.insert()
        values = {
            "IsConnect" : str(SystemConfiguration.IsConnect),
            "CreateAt": str(datetime.datetime.now())
        }
        await self.__context.execute(query=ins, values=values)

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