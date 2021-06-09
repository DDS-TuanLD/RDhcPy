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
from BaseServices.httpServices import HttpServices
env_path = Path('.')/'.env'
config = dotenv.load_dotenv(dotenv_path=env_path)


def main():
    httpServices = HttpServices()
    req = httpServices.CreateNewHttpRequest("aaaaaa", "sfbgsejgb")
    print(req.Url)
    
    
main()

