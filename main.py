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
from BaseServices.mqttServices import MqttServices

start_time = time.time()

env_path = Path('.')/'.env'
config = dotenv.load_dotenv(dotenv_path=env_path)

async def test2():
    while True:
        await asyncio.sleep(1)

async def main():
    mqtt = MqttServices()
    mqtt.MqttConnect()
    mqtt.MqttStartLoop()

    task1 = asyncio.ensure_future(test2())
    await task1

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
# asyncio.run(main())