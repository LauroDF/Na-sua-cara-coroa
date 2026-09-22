import asyncio
import json
from websockets import serve, Server, ServerConnection
from pydantic import TypeAdapter, ValidationError

from ..logger import init_logger

from ..protocol import (
    ClientMessage,
    JoinRoomProtocol,
    CreateRoomProtocol,
    ResponseProtocol,
)


class Host:
    
    def __init__(
        self,
        host: str = '0.0.0.0',
        port: int = 8000,
    ) -> None:
        self._host = host
        self._port = port
        
        self._server : Server | None = None
        self._logger = init_logger('host')
        self._message_adapter = TypeAdapter(ClientMessage)
        
    
    async def _handle_conn(self, websocket: ServerConnection) -> None:
        
        self._logger.info(f'Client connected {websocket.remote_address}')
        
        async for message in websocket:
            try:
                message = self._message_adapter.validate_json(message)
                
                if isinstance(message, CreateRoomProtocol):
                    self._logger.info(f'{websocket.remote_address} asked to create a room')
                    
                if isinstance(message, JoinRoomProtocol):
                    self._logger.info(f'{websocket.remote_address} asked to join room {message.room_id}')
            
                await self._send_message(websocket, f'Rapaaaiz')
            except ValidationError as exc:
                await self._send_message(
                    websocket,
                    json.dumps(
                        ResponseProtocol(
                            status='error',
                            message=str(exc)
                        )
                    )
                )
        
        self._logger.info(f'Client disconnected {websocket.remote_address}')
        
        
    async def _send_message(self, websocket: ServerConnection, message: str):
        self._logger.info(f'Sending message to {websocket.remote_address}: {message}')
        
        await websocket.send(message)
        
        
    async def run(self):
        self.server = await serve(
            self._handle_conn,
            self._host,
            self._port,
        )

        self._logger.info(f"Server running on ws://{self._host}:{self._port}")
        
        await self.server.serve_forever()
        
