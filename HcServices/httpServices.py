import Constant.constant as const
from requests.exceptions import HTTPError
from requests.structures import CaseInsensitiveDict
import asyncio
import aiohttp
import logging
class HttpRequest():
    __header: CaseInsensitiveDict
    __body: dict
    __url: str
    __cookie: dict
    
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
    
    __logger: logging.Logger
    
    def __init__(self, log: logging.Logger):
        self.__logger = log
    
    def CreateNewHttpHeader(self, token: str = "", endProfileId: str = "", cookie: str = ""):
        newHttpHeader = CaseInsensitiveDict()
        newHttpHeader["Accept"] = "application/json"
        newHttpHeader["Authorization"] = "Bearer " + token
        newHttpHeader["X-EndUserProfileId"] = endProfileId
        newHttpHeader["Cookie"] = cookie
        return newHttpHeader
    
    def CreateNewHttpRequest(
        self, url: str = None, body_data: dict = {}, header: CaseInsensitiveDict = {}):
        """ Create new http request

        Args:
            url (str): [url want to request]
            body_data (dict): [body of request]
            cookie (dict): [cookie of request] 
        Returns:
            [HttpRequest]: [new HttpRequest instance]
        """
        
        newHttpRequest = HttpRequest()
        newHttpRequest.Body = body_data
        newHttpRequest.Header = header
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
            async with session.get(req.Url, headers=req.Header, json=req.Body) as resp:
                resp.raise_for_status()
                await resp.json()
        except HTTPError as err:  
            return ""
        except Exception as err:
            return ""
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
        try:
            async with session.post(req.Url, headers=req.Header, json=req.Body) as resp:
                resp.raise_for_status()
                await resp.json()
                return resp
        except HTTPError as err:  
            return ""
        except Exception as err:
            return ""
    
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
            async with session.put(req.Url, headers=req.Header, json=req.Body) as resp:
                resp.raise_for_status()
                await resp.json()
        except HTTPError as err:  
            return ""
        except Exception as err:
            return ""
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
            async with session.delete(req.Url, headers=req.Header, json=req.Body) as resp:
                resp.raise_for_status()
                await resp.json()
        except HTTPError as err:  
            return ""
        except Exception as err:
            return ""
        return resp
    
    
