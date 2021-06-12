import unittest
from Database.Db import Db
import datetime

class TestDb(unittest.TestCase):
    db = Db()
    
    def __connect_db(self):
        self.db.createTable()
        self.db.DbRepoUpdate()
        
    def TestCreate(self):
        self.__connect_db()
        with self.assertRaises(TypeError):
            self.db.DbSystemConfigurationRepo.CreateWithParams(IsConnect="True", DisconnectTime=datetime.datetime.now())
            
if __name__ == '__main__':
    unittest.main(verbosity=2) 