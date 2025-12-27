import httpx
from zeep import AsyncClient
from zeep.transports import AsyncTransport


class WSFEClientManager:
    _instance = None
    _client = None

    def __new__(cls, wsdl):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, wsdl):
        if self.__class__._client is None:

            self.httpx_client = httpx.AsyncClient(timeout=20.0)
            self.transport = AsyncTransport(client=self.httpx_client)
            self.__class__._client = AsyncClient(wsdl=wsdl, transport=self.transport)

    def get_client(self): 
        return self.__class__._client

    async def close(self) -> None:
        if self.__class__._client:
            await self.httpx_client.aclose()
