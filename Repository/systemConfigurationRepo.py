from Model.systemConfiguration import systemConfigurationTable, systemConfiguration
from databases import Database
from sqlalchemy.orm import base
from sqlalchemy import Table
import sqlalchemy
from sqlalchemy.sql.expression import BinaryExpression
import asyncio
import datetime
class systemConfigurationRepo():
    __systemConfigurationTable: Table
    __context: Database
    
    def __init__(self, SystemConfigurationTable: Table, context: Database):
        self.__systemConfigurationTable = SystemConfigurationTable
        self.__context = context
    
    async def Create(self, IsConnect: bool=None):
        ins = self.__systemConfigurationTable.insert()
        values = {
            "IsConnect" : str(IsConnect),
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
    
    async def FindWithConditionAsync(self, condition: BinaryExpression):
        ins = self.__systemConfigurationTable.select().where(condition)
        rel = await self.__context.fetch_all(ins)
    
    async def FindWithConditionIterate(self, condition: BinaryExpression):
        ins = self.__systemConfigurationTable.select().where(condition)
        async for row in self.__context.iterate(query = ins):
            print(row)
      
