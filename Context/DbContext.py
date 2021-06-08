from abc import ABCMeta, ABC

class IContext(ABCMeta):
    pass

class MySqlDbContext(metaclass=IContext):
    pass
