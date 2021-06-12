from Controller.hcController import HcController
import asyncio
import requests
from Database.Db import Db

         
async def main():  
    db = Db()
    db.createTable()
    await db.DbConnect()
    db.DbRepoUpdate()
    
    hc = HcController()
    await hc.HcServicesRun()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())


