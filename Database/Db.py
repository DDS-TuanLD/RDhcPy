from databases import Database
import asyncio
class MetaDb(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaDb, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Db(metaclass= MetaDb):
    __context: Database
    
    @property
    def DbContext(self):
        return self.__context
    
    async def connectToDb(self):
        DATABASE_URL = "sqlite:///Testing.db"
        self.__context = Database(DATABASE_URL)
        await self.__context.connect()
        return self
    
    async def query(self):
        query = "INSERT INTO HighScores(name, score) VALUES (:name, :score)"
        values = [
            {"name": "mai", "score": 92},
            {"name": "dfds", "score": 87},
            {"name": "Cardsfdol", "score": 43},
        ]
        await self.__context.execute_many(query=query, values=values)
