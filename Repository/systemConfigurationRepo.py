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
    
    async def CreateWithParamsAsync(self, IsConnect: bool, DisconnectTime: datetime.datetime, ReconnectTime: datetime.datetime):
        """[summary]

        Args:
            IsConnect (bool): [description]
        """
        ins = self.__systemConfigurationTable.insert()
        values = {
            "IsConnect" : str(IsConnect),
            "DisconnectTime": DisconnectTime,
            "ReconnectTime": ReconnectTime,
            "CreateAt": datetime.datetime.now()
        }
        await self.__context.execute(query=ins, values=values)

    async def RemoveByIdAsync(self, id:int):
        """[summary]

        Args:
            id (int): [description]
        """
        ins = self.__systemConfigurationTable.delete().where(self.__systemConfigurationTable.c.id == id)
        await self.__context.execute(query=ins)
        
    async def RemoveByConditionAsync(self, systemConfiCondition: BinaryExpression):
        """[summary]

        Args:
            systemConfiCondition (BinaryExpression): [description]
        """
        ins = self.__systemConfigurationTable.delete().where(systemConfiCondition)
        await self.__context.execute(query=ins)
    
    async def UpdateByIdAsync(self, id:int, IsConnect: str, DisConnectime: datetime.datetime, ReConnectTime: datetime.datetime):
        """[summary]

        Args:
            id (int): [description]
        """
        ins = self.__systemConfigurationTable.update().where(self.__systemConfigurationTable.c.id == id).values(IsConnect = IsConnect, Disconnectime = DisConnectime, ReconnectTime = ReConnectTime, UpdateAt = datetime.datetime.now())
        await self.__context.execute(query=ins)
    
    async def FindwithIdAsync(self, id:int):
        """[summary]

        Args:
            id (int): [description]

        Returns:
            [type]: [description]
        """
        ins = self.__systemConfigurationTable.select().where(self.__systemConfigurationTable.c.id == id)
        rel = await self.__context.fetch_one(ins)
        return rel
    
    async def FindWithConditionAsync(self, condition: BinaryExpression):
        """[summary]

        Args:
            condition (BinaryExpression): [description]

        Returns:
            [type]: [description]
        """
        ins = self.__systemConfigurationTable.select().where(condition)
        rel = await self.__context.fetch_all(ins)
        return rel
    
    async def FindAllAsync(self):
            """[summary]

            Returns:
                [type]: [description]
            """
            ins = self.__systemConfigurationTable.select()
            rel = await self.__context.fetch_all(query=ins)
            return rel