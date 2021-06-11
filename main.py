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
from databases import Database
import sqlalchemy
from sqlalchemy.sql.expression import BinaryExpression

env_path = Path('.')/'.env'
config = dotenv.load_dotenv(dotenv_path=env_path)

         
async def main():  
    db = Db()
    db.createTable()
    await db.DbConnect()
    db.DbRepoUpdate()
    
    hc = HcController()
    await hc.HcServicesRun()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())


