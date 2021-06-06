import requests
import Constant.constant as const
from requests.exceptions import HTTPError
from requests.structures import CaseInsensitiveDict
import asyncio
import aiohttp
import os

class HttpRequest():
    __header: CaseInsensitiveDict
    __cookie: dict
    __body: dict
    __url: str
    
    def SetHeader(self, header: CaseInsensitiveDict):
        self.__header = header
        return self
    
    def SetCookie(self, cookie: dict):
        self.__cookie = cookie
        return self
    
    def SetBody(self, body: dict):
        self.__body = body
        return self
    
    def SetUrl(self, url: str):
        self.__url = url
        return self
    
    def GetHeader(self):
        return self.__header
    
    def GetCookie(self):
        return self.__cookie
        
    def GetBody(self):
        return self.__body
    
    def GetUrl(self):
        return self.__url    
class HttpServices():

    def CreateNewHttpRequest(
        self, url: str = None, cookie: dict = {}, token: str = "", body_data: dict = {}):
        """ Create new http request

        Args:
            url (str): [url want to request]
            cookie (dict): [cookie of request]
            token (str): [jwt token of request]
            body_data (dict): [body of request]

        Returns:
            [HttpRequest]: [new HttpRequest instance]
        """
        newHttpHeader = CaseInsensitiveDict()
        newHttpHeader["Accept"] = "application/json"
        newHttpHeader["Authorization"] = "Bearer " + token
        
        newHttpRequest = HttpRequest()
        newHttpRequest.SetBody(body_data).SetCookie(cookie).SetHeader(newHttpHeader).SetUrl(url)
        return newHttpRequest

    async def UseGetRequest(
        self, session: aiohttp.ClientSession, req: HttpRequest):
        """ Send get request

        Args:
            session (aiohttp.ClientSession): [aiohttp session]
            req (HttpRequest): [request]

        Returns:
            [ClientResponse]: [response of request]
        """
        resp = None
        try:
            async with session.get(req.GetUrl(), cookies=req.GetCookie(), headers=req.GetHeader(), data=req.GetBody()) as resp:
                resp.raise_for_status()
                await resp.json()
        except HTTPError as err:  
            print("Http request error: " + err)
        except Exception as err:
            print(f"Other exception: {err}")
        return resp

    async def UsePostRequest(
        self, session: aiohttp.ClientSession, req: HttpRequest):
        """ Send post request

        Args:
            session (aiohttp.ClientSession): [aiohttp session]
            req (HttpRequest): [request]

        Returns:
            [ClientResponse]: [response of request]
        """
        resp = None
        try:
            async with session.post(req.GetUrl(), cookies=req.GetCookie(), headers=req.GetHeader(), data=req.GetBody()) as resp:
                resp.raise_for_status()
                await resp.json()
        except HTTPError as err:  
            print("Http request error: " + err)
        except Exception as err:
            print(f"Other exception: {err}")
        return resp
    
    async def UsePutRequest(
        self, session: aiohttp.ClientSession, req: HttpRequest):
        """ Send put request

        Args:
            session (aiohttp.ClientSession): [aiohttp session]
            req (HttpRequest): [request]

        Returns:
            [ClientResponse]: [response of request]
        """
        resp = None
        try:
            async with session.put(req.GetUrl(), cookies=req.GetCookie(), headers=req.GetHeader(), data=req.GetBody()) as resp:
                resp.raise_for_status()
                await resp.json()
        except HTTPError as err:  
            print("Http request error: " + err)
        except Exception as err:
            print(f"Other exception: {err}")
        return resp

    async def UseDeleteRequest(
        self, session: aiohttp.ClientSession, req: HttpRequest):
        """ Send delete request

        Args:
            session (aiohttp.ClientSession): [aiohttp session]
            req (HttpRequest): [request]

        Returns:
            [ClientResponse]: [response of request]
        """
        resp = None
        try:
            async with session.delete(req.GetUrl(), cookies=req.GetCookie(), headers=req.GetHeader(), data=req.GetBody()) as resp:
                resp.raise_for_status()
                await resp.json()
        except HTTPError as err:  
            print("Http request error: " + err)
        except Exception as err:
            print(f"Other exception: {err}")
        return resp

        