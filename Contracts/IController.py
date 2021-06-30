from abc import ABC, ABCMeta, abstractmethod
import asyncio
import logging
class IController(metaclass=ABCMeta):
    
    @abstractmethod
    async def ActionDb(self):
        return
    
    @abstractmethod
    async def ActionNoDb(self):
        return