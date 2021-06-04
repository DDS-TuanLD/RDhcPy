from BaseServices.httpServices import HttpServices
import aiohttp
import os

class HcRequestServices():
    RefreshToken=""
    Token=""
    async def GetRefeshToken(self):
        rTokenUrl = os.getenv('REFRESH_TOKEN_URL')
        session = aiohttp.ClientSession()
        if rTokenUrl == "":
            self.RefreshToken ==  os.getenv("REFRESH_TOKEN")
            await session.close()
            return self
        res = await HttpServices().UseGetRequest(session, url=rTokenUrl)
        try:
            rTokenJson = await res.json()
            self.RefreshToken = rTokenJson["RefreshToken"]
        except Exception as err:
            print(f"Exception when get refresh token: {err}")
        await session.close()
        return self

    async def GetToken(self):
        TokenUrl = os.getenv('TOKEN_URL')
        session = aiohttp.ClientSession()
        cookie = {"RefreshToken": os.getenv('REFRESH_TOKEN')}
        print(cookie)
        res = await HttpServices().UseGetRequest(session, url=TokenUrl, cookie=cookie)
        try:
            TokenJson = await res.json()
            self.Token = TokenJson["Token"]
        except Exception as err:
            print(f"Exception when get token: {err}")
        await session.close()
        return self

    async def GetServerRequest(self, url):
        session = aiohttp.ClientSession()
        rel=""
        res = await HttpServices().UseGetRequest(session, url=url, token=self.Token)
        try:
            rel = await res.json()
        except Exception as err:
            print(f"Exception when get refresh token: {err}")
        session.close()
        return rel

    async def PostServerRequest(self, url, data):
        session = aiohttp.ClientSession()
        rel=""
        res = await HttpServices().UsePostRequest(session, url=url, data=data, token=self.Token)
        try:
            rel = await res.json()
        except Exception as err:
            print(f"Exception when get refresh token: {err}")
        session.close()
        return rel

    async def PutServerRequest(self, url, data):
        session = aiohttp.ClientSession()
        rel=""
        res = await HttpServices().UsePutRequest(session, url=url, data=data, token=self.Token)
        try:
            rel = await res.json()
        except Exception as err:
            print(f"Exception when get refresh token: {err}")
        session.close()
        return rel

    async def DelServerRequest(self, url, data):
        session = aiohttp.ClientSession()
        rel=""
        res = await HttpServices().UseDeleteRequest(session, url=url, data=data, token=self.Token)
        try:
            rel = await res.json()
        except Exception as err:
            print(f"Exception when get refresh token: {err}")
        session.close()
        return rel
