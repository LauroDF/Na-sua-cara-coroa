from pydantic import BaseModel, Field, TypeAdapter
from dataclasses import dataclass
from typing import Literal, Annotated, Any

from .schemas import CoinChoice


class CreateRoomProtocol(BaseModel):
    type: Literal['create_room']
    
    
class JoinRoomProtocol(BaseModel):
    type: Literal['join_room']
    room_id: str
    
    
class CoinChoiceProtocol(BaseModel):
    type: Literal['coin_choice']
    choice: CoinChoice
    
    
class RematchProtocol(BaseModel):
    type: Literal['rematch']
    accept: bool

    
@dataclass(frozen=True, slots=True)
class ResponseProtocol:
    status: Literal['ok', 'error']
    message: Any
    
    
ClientMessage = Annotated[
    CreateRoomProtocol | 
    JoinRoomProtocol |
    CoinChoiceProtocol |
    RematchProtocol
    ,
    Field(discriminator='type')
]