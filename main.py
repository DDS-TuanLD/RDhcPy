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

def main_thread(db: Db, hc: HcController):
    db.DbCreateTable()
    db.DbServicesInit() 
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(hc.HcServicesRun())
    loop.close()
    
def mqtt_reconnect_thread(hc: HcController):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(hc.HcCheckMqttConnect())
    loop.close()
    
def main():  
    thread1 = threading.Thread(target = main_thread, args=(db, hc,))
    thread2 = threading.Thread(target = mqtt_reconnect_thread, args=(hc,))

    thread1.start()
    thread2.start()
    
    thread1.join() 
    thread2.join()
  
if __name__ == "__main__":
    main()