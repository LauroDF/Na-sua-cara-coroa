import json
from websockets.asyncio.server import ServerConnection
from dataclasses import asdict
from uuid import UUID

from ..protocols import ResponseProtocol


class ClientSession:
    def __init__(self, id: UUID, websocket: ServerConnection) -> None:
        self.id = id
        self._websocket = websocket
        self._room_id: str | None = None
        
        
    def connect_to_room(self, room_id: str):
        self._room_id = room_id
        
        
    def disconnect_from_room(self):
        self._room_id = None
        
        
    async def send_message(self, message: ResponseProtocol):
        await self._websocket.send(json.dumps(asdict(message)))
        
        
    @property
    def websocket(self) -> ServerConnection:
        return self._websocket
    
    
    @property
    def room_id(self) -> str:
        return self._room_id