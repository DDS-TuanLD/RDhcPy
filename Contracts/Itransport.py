from abc import ABC, ABCMeta, abstractmethod
import asyncio

class Itransport(metaclass=ABCMeta):
    
    @abstractmethod
    def Init(self):
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
    