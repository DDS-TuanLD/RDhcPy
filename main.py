from Controller.hcController import HcController
import asyncio
import time
import json
import aiohttp
from aiohttp import ClientSession
import requests
import dotenv
from pathlib import Path
import os
from Database.Db import Db
from Model.users import users
from databases import Database

env_path = Path('.')/'.env'
config = dotenv.load_dotenv(dotenv_path=env_path)

         
async def main():  
    db = Db()
    hc = HcController()

    db.createTable()
    await db.DbConnect()
    await hc.HcServicesRun()
    
loop = asyncio.get_event_loop()
loop.run_until_complete(main())


