from abc import ABCMeta, abstractmethod


class IHandler(metaclass=ABCMeta):
    @abstractmethod
    def handler(self, item):
        pass
