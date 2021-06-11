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
    
    async def CreateWithParamsAsync(self, IsConnect: bool):
        ins = self.__systemConfigurationTable.insert()
        values = {
            "IsConnect" : str(IsConnect),
        }
        await self.__context.execute(query=ins, values=values)

    async def RemoveAsyncById(self, id:int):
        ins = self.__systemConfigurationTable.delete().where(self.__systemConfigurationTable.c.id == id)
        await self.__context.execute(query=ins)
        
    async def RemoveAsyncByCondition(self, condition: BinaryExpression):
        ins = self.__systemConfigurationTable.delete().where(condition)
        await self.__context.execute(query=ins)
    
    async def UpdateAsync(self, id:int):
        ins = self.__systemConfigurationTable.update().where(self.__systemConfigurationTable.c.id == id).values(IsConnect = "False")
        await self.__context.execute(query=ins)
    
    async def FindAllAsync(self):
        pass
    
    async def FindWithConditionAsync(self, condition: BinaryExpression):
        ins = self.__systemConfigurationTable.select().where(condition)
        rel = await self.__context.fetch_all(ins)
    
