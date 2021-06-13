from Controller.hcController import HcController
import asyncio
import requests
from Database.Db import Db
import datetime
from Model.systemConfiguration import systemConfiguration
         
async def main():  
    db = Db()
    db.DbCreateTable()
    db.DbServicesInit()
  
    hc = HcController()
    await hc.HcServicesRun()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())


