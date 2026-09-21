import asyncio
from uuid import uuid4
from websockets.asyncio.client import ClientConnection, connect

from ..logger import init_logger


class Client:
    
    def __init__(self, uri: str = "ws://localhost:8000") -> None:
        self._uri = uri
        self._id = str(uuid4())
        
        self._websocket: ClientConnection | None = None
        self._logger = init_logger(f'client {self._id}')
        
    
    async def _connect(self):
        self._websocket = await connect(self._uri)
        
        self._logger.info(f'Conected to {self._uri}')
        
        
    async def run(self):
        await self._connect()
        
        if self._websocket is None:
            raise RuntimeError("Unable to connect to the server")
        
        await self._websocket.wait_closed()
        
        
    async def disconnect(self):
        if self._websocket is not None:
            await self._websocket.close()
        