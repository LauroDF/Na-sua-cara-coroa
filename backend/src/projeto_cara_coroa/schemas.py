from dataclasses import dataclass
from pydantic import BaseModel
from typing import Literal, TypeAlias


CoinChoice: TypeAlias = Literal['heads', 'tails']


@dataclass(frozen=True, slots=True)
class RoomResponseDTO:
    room_id: str
    
    
@dataclass(slots=True)
class RoundResult:
    status: Literal['next_round', 'game_finish']
    host_score: int
    guest_score: int
    result: CoinChoice


@dataclass(slots=True)
class RematchResponse:
    result: Literal['accepted', 'declined']
