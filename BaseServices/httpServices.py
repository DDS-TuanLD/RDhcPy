import requests
import Constant.constant as const
from requests.exceptions import HTTPError
from requests.structures import CaseInsensitiveDict
import asyncio
import aiohttp
import os

class HttpRequest():
    __header: CaseInsensitiveDict
    __body: dict
    __url: str
    
    @property
    def Body(self):
        return self.__body
    
    @property
    def Header(self):
        return self.__header
    
    @property 
    def Url(self):
        return self.__url
        
    @Header.setter
    def Header(self, header: CaseInsensitiveDict):
        self.__header = header
        return self
    
    @Body.setter
    def Body(self, body: dict):
        self.__body = body
        return self
    
    @Url.setter
    def Url(self, url: str):
        self.__url = url
        return self
    
  
class HttpServices():

    def CreateNewHttpRequest(
        self, url: str = None, token: str = "", body_data: dict = {}):
        """ Create new http request

        Args:
            url (str): [url want to request]
            token (str): [jwt token of request]
            body_data (dict): [body of request]

        Returns:
            [HttpRequest]: [new HttpRequest instance]
        """
        newHttpHeader = CaseInsensitiveDict()
        newHttpHeader["Accept"] = "application/json"
        newHttpHeader["Authorization"] = "Bearer " + token
        
        newHttpRequest = HttpRequest()
        newHttpRequest.Body = body_data
        newHttpRequest.Header = newHttpHeader
        newHttpRequest.Url = url
        
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
            async with session.get(req.Url, headers=req.Header, data=req.Body) as resp:
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
            async with session.post(req.Url, headers=req.Header, data=req.Body) as resp:
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
            async with session.put(req.Url, headers=req.Header, data=req.Body) as resp:
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
            async with session.delete(req.Url, headers=req.Header, data=req.Body) as resp:
                resp.raise_for_status()
                await resp.json()
        except HTTPError as err:  
            print("Http request error: " + err)
        except Exception as err:
            print(f"Other exception: {err}")
        return resp

        