from websockets.asyncio.server import ServerConnection
from uuid import UUID


class ClientSession:
    def __init__(self, id: UUID, websocket: ServerConnection) -> None:
        self.id = id
        self._websocket = websocket
        self._room_id: str | None = None
        
        
    def connect_to_room(self, room_id: str):
        self._room_id = room_id
        
        
    @property
    def websocket(self) -> ServerConnection:
        return self._websocket