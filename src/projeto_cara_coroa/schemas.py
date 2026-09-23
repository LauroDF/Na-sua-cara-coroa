from dataclasses import dataclass
from pydantic import BaseModel

@dataclass(frozen=True, slots=True)
class RoomResponseDTO:
    room_id: str