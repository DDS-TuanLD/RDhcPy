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

start_time = time.time()
env_path = Path('.')/'.env'
config = dotenv.load_dotenv(dotenv_path=env_path)

async def main():
    Hc = HcController()
    session = aiohttp.ClientSession()
    for number in range(1, 31):
        pokemon_url = f'https://pokeapi.co/api/v2/pokemon/{number}'
        res = await Hc.httpServices.UseGetRequest(session, url=pokemon_url)
        try:
            pokemon = await res.json()
            print(pokemon["name"])
        except Exception as err:
            print(f"json parse exception: {err}")
    await session.close()

asyncio.run(main())
print("--- %s seconds ---" % (time.time() - start_time))