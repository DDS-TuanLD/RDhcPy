from abc import ABC, ABCMeta, abstractmethod
import asyncio

class Itransport(metaclass=ABCMeta):
    
    @abstractmethod
    async def Init(self):
        return
    
    @abstractmethod
    def Listen(self):
        return
    
    @abstractmethod
    def DisConnect(self):
        return
    
    @abstractmethod
    def ReConnect(self):
        return
    
    @abstractmethod
    def Send(self):
        return
    
    @abstractmethod
    def Receive(self):
        return
    @abstractmethod
    def HandlerData(self, data):
        return
        