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

env_path = Path('.')/'.env'
config = dotenv.load_dotenv(dotenv_path=env_path)

async def main():  
    hc = HcController() 
    await hc.HcServicesRun()
    
loop = asyncio.new_event_loop()
loop.run_until_complete(main())