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

async def other_coroutine(hc):
    while True:
        await asyncio.sleep(1)
        print("This is other coroutine")

async def mqtt_coroutine(hc):
    mqtt = hc.mqttServices
    mqtt.MqttConnect()
    while True:
        await asyncio.sleep(0.1)
        mqtt.MqttStartLoop()

async def main():
    hc = HcController()
    task1 = asyncio.ensure_future(mqtt_coroutine(hc))
    task2 = asyncio.ensure_future(other_coroutine(hc))
    await asyncio.gather(task1, task2)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
