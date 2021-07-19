from abc import ABC, ABCMeta, abstractmethod
import asyncio
import queue


class ITransport(metaclass=ABCMeta):
    receive_data_queue: queue.Queue

    def __init__(self):
        self.receive_data_queue = queue.Queue()

    @abstractmethod
    def connect(self):
        return
    
    @abstractmethod
    def disconnect(self):
        return
    
    @abstractmethod
    def reconnect(self):
        return
    
    @abstractmethod
    def send(self, destination, send_data):
        return
    
    @abstractmethod
    def receive(self):
        return
