class IHttpBaseServices:
    async def UseGetRequest(self, session, url="", cookie="", token=""):
        pass
    
    async def UsePostRequest(self, session, url="", data="", cookie="", token=""):
        pass

    async def UsePutRequest(self, session, url="", data="", token=""):
        pass

    async def UseDeleteRequest(self, session, url="", data="", token=""):
        pass
