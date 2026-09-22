import asyncio
from uuid import uuid4
from websockets.asyncio.client import ClientConnection, connect
from random import randint

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
        
    
    async def _send_message(self, message: str):
        await self._websocket.send(message)
        
        
    async def _receive_messages(self):
        async for message in self._websocket:
            pass    
        
    async def run(self):
        await self._connect()

        receiver_task = asyncio.create_task(
            self._receive_messages()
        )

        await self._send_message("Hello server")
        
        await asyncio.sleep(randint(1,5))

        await self._send_message("Another message")

        await asyncio.sleep(randint(1,5))

        receiver_task.cancel()
        
        await self.disconnect()
        
        
    async def disconnect(self):
        if self._websocket is not None:
            await self._websocket.close()
        