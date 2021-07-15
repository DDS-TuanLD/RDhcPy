from abc import ABC, ABCMeta, abstractmethod
import asyncio
import logging
class IController(metaclass=ABCMeta):
    
    @abstractmethod
    def Run(self):
        return
    