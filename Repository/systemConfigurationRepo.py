from Model.systemConfiguration import systemConfigurationTable, systemConfiguration
from sqlalchemy import Table, select
import sqlalchemy
from sqlalchemy.sql.expression import BinaryExpression
import asyncio
import datetime
from sqlalchemy.engine.base import Connection

class systemConfigurationRepo():
    __systemConfigurationTable: Table
    __context: Connection
    
    def __init__(self, SystemConfigurationTable: Table, context: Connection):
        self.__systemConfigurationTable = SystemConfigurationTable
        self.__context = context
    
    def CreateWithParams(self, IsConnect: bool, DisconnectTime: datetime.datetime, ReconnectTime: datetime.datetime):
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
        self.__context.execute(ins, values)

    def RemoveById(self, id:int):
        """[summary]

        Args:
            id (int): [description]
        """
        ins = self.__systemConfigurationTable.delete().where(self.__systemConfigurationTable.c.Id == id)
        self.__context.execute(ins)
        
    def RemoveByCondition(self, systemConfiCondition: BinaryExpression):
        """[summary]

        Args:
            systemConfiCondition (BinaryExpression): [description]
        """
        ins = self.__systemConfigurationTable.delete().where(systemConfiCondition)
        self.__context.execute(ins)
    
    def UpdateById(self, id:int, IsConnect: str, DisConnectTime: datetime.datetime, ReConnectTime: datetime.datetime):
        """[summary]

        Args:
            id (int): [description]
        """
        ins = self.__systemConfigurationTable.update().where(self.__systemConfigurationTable.c.Id == id).values(IsConnect = IsConnect, DisconnectTime = DisConnectTime, ReconnectTime = ReConnectTime, UpdateAt = datetime.datetime.now())
        self.__context.execute(ins)
    
    def FindwithId(self, Id:int):
        """[summary]

        Args:
            id (int): [description]

        Returns:
            [type]: [description]
        """
        ins = self.__systemConfigurationTable.select().where(self.__systemConfigurationTable.c.Id == Id)
        rel = self.__context.execute(ins)
        return rel
            
    def FindWithCondition(self, condition: BinaryExpression):
        """[summary]

        Args:
            condition (BinaryExpression): [description]

        Returns:
            [type]: [description]
        """
        ins = self.__systemConfigurationTable.select().where(condition)
        rel = self.__context.execute(ins)
        return rel
    
    def FindAll(self):
            """[summary]

            Returns:
                [type]: [description]
            """
            ins = self.__systemConfigurationTable.select()
            rel = self.__context.execute(ins)
            return rel