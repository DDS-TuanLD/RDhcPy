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
url1 = 'http://httpbin.org/cookies'
cookies = {'cookies_are': 'working'}

         
async def main():  
    cookie = f"RefreshToken={refreshToken}"
    hc = HcController() 
    header = hc.HcHttpServices.CreateNewHttpHeader(cookie = cookie)
    req = hc.HcHttpServices.CreateNewHttpRequest(url=url, header=header)
    async with ClientSession(cookies=cookies) as session:
        async with session.get(url) as resp:
            print(resp)
   
loop = asyncio.new_event_loop()
loop.run_until_complete(main())


