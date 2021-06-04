import requests
import Constant.constant as const
from requests.exceptions import HTTPError
from requests.structures import CaseInsensitiveDict
import asyncio
import aiohttp
import os

class HttpServices():

    async def UseGetRequest(self, session, url="", cookie="", token=""):
        headers = CaseInsensitiveDict();
        headers["Accept"] = "application/json"
        headers["Authorization"] = "Bearer " + token
        resp=""
        try:
            async with session.get(url, cookies=cookie, headers=headers) as resp:
                resp.raise_for_status()
                await resp.json()
        except HTTPError as err:  
            print("Http request error: " + err)
        except Exception as err:
            print(f"Other exception: {err}")
        return resp

    async def UsePostRequest(self, session, url="", data="", cookie="", token=""):
        headers = CaseInsensitiveDict();
        headers["Accept"] = "application/json"
        headers["Authorization"] = "Bearer " + token
        resp=""
        try:
            async with session.post(url, headers=headers, data=data, cookies=cookie, token=token) as resp:
                resp.raise_for_status()
                resp.json()
        except HTTPError as err:  
            print("Http request error: " + err)
        except Exception as err:
            print(f"Other exception: {err}")
        return resp
    
    async def UsePutRequest(self, session, url="", data="", token=""):
        headers = CaseInsensitiveDict();
        headers["Accept"] = "application/json"
        headers["Authorization"] = "Bearer " + token
        resp=""
        try:
            async with session.put(url, headers=headers, data=data, token=token) as resp:
                resp.raise_for_status()
                resp.json()
        except HTTPError as err:  
            print("Http request error: " + err)
        except Exception as err:
            print(f"Other exception: {err}")
        return resp

    async def UseDeleteRequest(self, session, url="", data="", token=""):
        headers = CaseInsensitiveDict();
        headers["Accept"] = "application/json"
        headers["Authorization"] = "Bearer " + token
        resp=""
        try:
            async with session.delete(url, headers=headers, data=data, token=token) as resp:
                resp.raise_for_status()
                resp.json()
        except HTTPError as err:  
            print("Http request error: " + err)
        except Exception as err:
            print(f"Other exception: {err}")
        return resp

        