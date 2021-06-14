from Controller.hcController import HcController
import asyncio
import requests
from Database.Db import Db
import datetime
from Model.systemConfiguration import systemConfiguration
import threading        
# async def main():  
#     db = Db()
#     db.DbCreateTable()
#     db.DbServicesInit()
    
#     hc = HcController()
#     await hc.HcServicesRun()

# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())


db = Db()
hc = HcController()

def thr(db: Db, hc: HcController):
    db.DbCreateTable()
    db.DbServicesInit() 
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(hc.HcServicesRun())
    loop.close()
    
def thr2(hc: HcController):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(hc.HcCheckMqttConnect())
    loop.close()
    
def main():  
    t = threading.Thread(target = thr, args=(db, hc))
    t2 = threading.Thread(target = thr2, args=(hc,))

    t.start()
    t2.start()
    
    t.join() 
    t2.join()
  
if __name__ == "__main__":
    main()