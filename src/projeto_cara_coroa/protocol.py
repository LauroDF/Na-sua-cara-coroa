from pydantic import BaseModel, Field, TypeAdapter
from dataclasses import dataclass
from typing import Literal, Annotated


class CreateRoomProtocol(BaseModel):
    type: Literal['create_room']
    
    
class JoinRoomProtocol(BaseModel):
    type: Literal['join_room']
    room_id: str
    
    
@dataclass(frozen=True, slots=True)
class ResponseProtocol:
    status: Literal['ok', 'error']
    message: str
    
    
ClientMessage = Annotated[
    CreateRoomProtocol | 
    JoinRoomProtocol,
    Field(discriminator='type')
]