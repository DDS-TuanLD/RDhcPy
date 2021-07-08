from abc import ABC, ABCMeta, abstractmethod
import asyncio
import logging

class Ihandler(metaclass=ABCMeta):
    @abstractmethod
    def Handler(self):
        pass