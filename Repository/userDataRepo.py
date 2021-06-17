from Model.userData import userData
from sqlalchemy import Table, select
import sqlalchemy
from sqlalchemy.sql.expression import BinaryExpression
import asyncio
import datetime
from sqlalchemy.engine.base import Connection

class userDataRepo():
    __userDataTable: Table
    __context: Connection
    
    def __init__(self, UserDataTable: Table, context: Connection):
        self.__userDataTable = UserDataTable
        self.__context = context
    
    def CreateWithParams(self, userData: userData):
        """[summary]

        Args:
            userData (userData): [description]
        """
        ins = self.__userDataTable.insert()
        values = {
            "RefreshToken" : userData.RefreshToken,
            "EndUserProfileId": userData.EndUserProfileId,
            "CreateAt": datetime.datetime.now()
        }
        self.__context.execute(ins, values)

    def RemoveById(self, id:int):
        """[summary]

        Args:
            id (int): [description]
        """
        ins = self.__userDataTable.delete().where(self.__userDataTable.c.Id == id)
        self.__context.execute(ins)
        
    def RemoveByCondition(self, userDataCondition: BinaryExpression):
       
        ins = self.__userDataTable.delete().where(userDataCondition)
        self.__context.execute(ins)
    
    def UpdateById(self, id:int, newUserData: userData):
        """[summary]

        Args:
            id (int): [description]
        """
        ins = self.__userDataTable.update().where(self.__userDataTable.c.Id == id).values({"RefreshToken": newUserData.RefreshToken,
                                                                                           "EndUserProfileId": newUserData.EndUserProfileId,
                                                                                           "UpdateAt": datetime.datetime.now()})
        self.__context.execute(ins)
    
    def FindwithId(self, Id:int):
        """[summary]

        Args:
            id (int): [description]

        Returns:
            [type]: [description]
        """
        ins = self.__userDataTable.select().where(self.__userDataTable.c.Id == Id)
        rel = self.__context.execute(ins)
        return rel
            
    def FindWithCondition(self, condition: BinaryExpression):
        """[summary]

        Args:
            condition (BinaryExpression): [description]

        Returns:
            [type]: [description]
        """
        ins = self.__userDataTable.select().where(condition)
        rel = self.__context.execute(ins)
        return rel
    
    def FindAll(self):
            """[summary]

            Returns:
                [type]: [description]
            """
            ins = self.__userDataTable.select()
            rel = self.__context.execute(ins)
            return rel