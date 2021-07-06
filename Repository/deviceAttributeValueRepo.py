from sqlalchemy import Table, select
import sqlalchemy
from sqlalchemy.sql.expression import BinaryExpression
import asyncio
import datetime
from sqlalchemy.engine.base import Connection

class deviceAttributeValueRepo():
    __deviceAttributeValue: Table
    __context: Connection
    
    def __init__(self, DeviceAttributeValueTable: Table, context: Connection):
        self.__deviceAttributeValue = DeviceAttributeValueTable
        self.__context = context
    
    def FindWithCondition(self, condition: BinaryExpression):
        """[summary]

        Args:
            condition (BinaryExpression): [description]

        Returns:
            [type]: [description]
        """
        ins = self.__deviceAttributeValue.select().where(condition)
        rel = self.__context.execute(ins)
        return rel