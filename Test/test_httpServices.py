import unittest
from Services.httpServices import HttpAsyncServices
import aiohttp
import asyncio
class TestHttpService(unittest.TestCase):
    
    async def test_getNewToken(self):
        refreshToken =  "10a8F5yStJ1A7JBXRzc4NdO67kxbZtbxGYQPyOFlQXiRR/nI9ZrTzAwCUYrq2DUnNyKrAFBE/PB3Oa8t9tGy57xKqBQPfpFhoNXVDB83JC8QsPCxxy2qIMdI2KlxthA7U8xx8v+iTJIzEMmOZUO6VLBUuKS1L2Kwiou/7HB+3gp2QgJRmF4WJiXkKFZzaCwyeOjOz/SYBTp6VG519IxGLCi3z+FUqWC32eP8BFlWQ3I="
        getNewTokenUrl = "https://iot-dev.truesight.asia/rpc/iot-ebe/account/renew-token"
        cookie = f"RefreshToken={refreshToken}"
        
        header = HttpAsyncServices.CreateNewHttpHeader(cookie=cookie)
        req = HttpAsyncServices.CreateNewHttpRequest(header=header, url=getNewTokenUrl)
        session = aiohttp.ClientSession()
        res = await HttpAsyncServices.UsePostRequest(session, req)
        data = await res.json()
        data = await res.json()
        token=""
        token = data['token'] 
        self.assertEqual(token, "", msg=f'{token}')
        
if __name__ == '__main__':
    unittest.main(verbosity=2)