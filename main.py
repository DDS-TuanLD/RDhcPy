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

refreshToken = "10a8F5yStJ1A7JBXRzc4NcF79tVLXdQMfiGbSU2teR6Xr4HBILV/a10JfkJltYMLmpnlnVHOs8A4s48uoTJnWDsZeEIWDt6BrRj1QNdr1qyJnOiNe9QKAovSaaKnYJ8lL9IVHGtuvPJDKgVttwoMLjUJVPOcbBaNdbGvy9B0dCDHOWAdLzHSR9LpVOxxVO0HUJPpcQNoSAJp1kdxca0YcCV6h+I7clw8k/HF2mfkqGwCv6jnRJXEmclVO/eVsIPG"
url = "https://iot-dev.truesight.asia/rpc/iot-ebe/account/renew-token"
async def main():  
    cookie = {"RefreshToken": refreshToken}
    hc = HcController() 
    header = hc.HcHttpServices.CreateNewHttpHeader(cookie = cookie)
    req = hc.HcHttpServices.CreateNewHttpRequest(url=url, header=header)
    session = aiohttp.ClientSession()
    res = await hc.HcHttpServices.UsePostRequest(session, req)
    print(req)
    await session.close()
    # await hc.HcServicesRun()
    # db = Db()
    # db.createTable()
    # await db.DbConnect()
    
    # ins = db.DbUserTable.insert()
    # values = [
    #     {"id": 10, "name": "False"},
    # ]
    # await db.DbContext.execute_many(query=ins, values=values)
    
loop = asyncio.new_event_loop()
loop.run_until_complete(main())


