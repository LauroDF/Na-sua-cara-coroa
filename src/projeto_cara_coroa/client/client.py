import asyncio
from uuid import uuid4
from websockets.asyncio.client import ClientConnection, connect
from random import randint
import json

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
        
    async def run(self, messages: list[tuple[dict[str, str], int, int]]):
        await self._connect()

        receiver_task = asyncio.create_task(
            self._receive_messages()
        )
        
        for message in messages:

            await self._send_message(json.dumps(
                message[0]
            ))
        
            await asyncio.sleep(randint(message[1], message[2]))
            
        receiver_task.cancel()
        
        await self.disconnect()
        
        
    async def disconnect(self):
        if self._websocket is not None:
            await self._websocket.close()
        