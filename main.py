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
from Context.DbContext import MySqlDbContext

env_path = Path('.')/'.env'
config = dotenv.load_dotenv(dotenv_path=env_path)

url = "https://iot-dev.truesight.asia/rpc/iot-ebe/account/renew-token"
url1 = 'http://httpbin.org/cookies'

cookie = {"RefreshToken": "10a8F5yStJ1A7JBXRzc4NdO67kxbZtbxGYQPyOFlQXiRR/nI9ZrTzAwCUYrq2DUnFt915wjAkXoGjGsIoL814I7fO5swdgc2xd6AV6WPwF/QBDt91QrHKPk/V39NkCETROCK4ik3FwXGO8g/rI9gHPZoY38zDzFlETKfhBd9LA0zBi+ULFs3gxSrcivsAbp2uUFQ/ie1b6Yu3J4tuRB2eQuMDHICbiAYsd67Rn38AL0="}


async def main():  
    context = MySqlDbContext()
    hc = HcController(context) 
    req = hc.HcHttpServices.CreateNewHttpRequest(url1)
    
    async with ClientSession(cookies=cookie) as session:
        async with session.get(url) as resp:
            print(resp)
            
    # session = aiohttp.ClientSession(cookies=cookie)
    # res = await hc.HcHttpServices.UseGetRequest(session, req)
    # print(res)
    # await session.close()
    
    # res = requests.post(url, cookies = cookie)
    # print(res.json())
    
loop = asyncio.new_event_loop()
loop.run_until_complete(main())