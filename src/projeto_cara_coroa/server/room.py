import asyncio
from dataclasses import asdict
from websockets.asyncio.client import ClientConnection

from ..client.session import ClientSession

from ..schemas import (
    RoomResponseDTO,
)

from ..protocols import (
    ResponseProtocol,
)


class Room:
    def __init__(self, id: str, host: ClientSession) -> None:
        self._id = id
        self._host: ClientSession = host
        self._guest: ClientSession | None = None
        
        
    def join_room(self, guest: ClientSession) -> ResponseProtocol:
        if self._guest is not None:
            return ResponseProtocol(
                status='error',
                message=f'Room {self._id} is already full.'
            )
            
        self._guest = guest 
        
        return ResponseProtocol(
            status='ok',
            message=asdict(RoomResponseDTO(
                room_id=self._id
            ))
        )
    