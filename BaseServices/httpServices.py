import requests
import Constant.constant as const
from requests.exceptions import HTTPError
from requests.structures import CaseInsensitiveDict
import asyncio
import aiohttp
from Contract.IHttpServices import IHttpBaseServices
import os

class HttpServices(IHttpBaseServices):

    async def UseGetRequest(self, session, url="", cookie="", token=""):
        headers = CaseInsensitiveDict();
        headers["Accept"] = "application/json"
        headers["Authorization"] = "Bearer " + token
        resp=""
        try:
            # async with session.get(url, headers=headers) as resp:
            #     resp.raise_for_status()
            #     await resp.json()
            resp = await session.get(url, headers=headers, cookies=cookie)
            resp.raise_for_status()
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
            resp = await session.post(url, headers=headers, data=data, cookies=cookie, token=token)
            resp.raise_for_status()
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
            resp = await session.put(url, headers=headers, data=data, token=token)
            resp.raise_for_status()
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
            resp = await session.delete(url, headers=headers, data=data, token=token)
            resp.raise_for_status()
        except HTTPError as err:  
            print("Http request error: " + err)
        except Exception as err:
            print(f"Other exception: {err}")
        return resp

        