from Context.DbContext import MySqlDbContext, IContext

class MetaDb(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaDb, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Db(metaclass= MetaDb):
        
    DbContext: IContext
    def __init__(self, MyContext: IContext):
        self.DbContext = MyContext
        
