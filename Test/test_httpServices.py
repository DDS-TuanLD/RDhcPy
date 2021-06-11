import unittest
from Services.httpServices import HttpAsyncServices
import aiohttp
import asyncio
import aiounittest
import http
class TestHttpService(aiounittest.AsyncTestCase):
    
    MESSAGE_FMT = 'want `{0}`, get `{1}`: `{2}`'
    refreshToken =  "10a8F5yStJ1A7JBXRzc4NdO67kxbZtbxGYQPyOFlQXiRR/nI9ZrTzAwCUYrq2DUnNyKrAFBE/PB3Oa8t9tGy57xKqBQPfpFhoNXVDB83JC8QsPCxxy2qIMdI2KlxthA7U8xx8v+iTJIzEMmOZUO6VLBUuKS1L2Kwiou/7HB+3gp2QgJRmF4WJiXkKFZzaCwyeOjOz/SYBTp6VG519IxGLCi3z+FUqWC32eP8BFlWQ3I="
    getNewTokenUrl = "https://iot-dev.truesight.asia/rpc/iot-ebe/account/renew-token"
    testPostMethodUrl = "https://iot-dev.truesight.asia/rpc/iot-ebe/sync/list-device-type"
    testPostMethodBodyData = {
        "updatedAt": "2021-06-11T14:14:02.733Z",
        "skip": 0,
        "take": 0,
        "orderType": 0
    }
    endProfileId="10033"
    httpService = HttpAsyncServices()

    async def __test_getNewToken(self):
        cookie = f"RefreshToken={self.refreshToken}"
        header = self.httpService.CreateNewHttpHeader(cookie=cookie)
        req = self.httpService.CreateNewHttpRequest(header=header, url=self.getNewTokenUrl)
        
        session = aiohttp.ClientSession()
        res = await self.httpService.UsePostRequest(session, req)
        data = await res.json()
        token=""
        token = data['token'] 
        return token    
        
    async def test_usePostRequest(self):
        expect = http.HTTPStatus.OK
        
        token = await self.__test_getNewToken()
        cookie = f"Token={token}"
        header = self.httpService.CreateNewHttpHeader(cookie=cookie, endProfileId= self.endProfileId)
        req = self.httpService.CreateNewHttpRequest(url=self.testPostMethodUrl, body_data=self.testPostMethodBodyData, header=header)
        
        session = aiohttp.ClientSession()
        res = await self.httpService.UsePostRequest(session, req)
        output = res.status
        msg = self.MESSAGE_FMT.format(expect, "res.status_code", output)
        self.assertEqual(output, expect, msg=msg)
        await session.close()
    