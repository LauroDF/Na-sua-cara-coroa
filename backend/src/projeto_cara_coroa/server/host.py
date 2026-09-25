import asyncio
import json
import string 
from dataclasses import asdict
from typing import Any
from uuid import uuid4, UUID
from random import choices
from websockets.asyncio.server import serve, Server, ServerConnection
from pydantic import TypeAdapter, ValidationError

from ..logger import init_logger

from .room import Room

from ..client.session import ClientSession

from ..protocols import (
    CoinChoice,
    ClientMessage,
    JoinRoomProtocol,
    CreateRoomProtocol,
    CoinChoiceProtocol,
    RematchProtocol,
    ResponseProtocol,
)

from ..schemas import (
    RoomResponseDTO
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
        self._logger = init_logger(__name__)
        self._message_adapter = TypeAdapter(ClientMessage)
        
        self._rooms: dict[str, Room] = {}
        self._sessions: dict[UUID, ClientSession] = {}
        
    
    def _create_random_code(self) -> str:
        pool = string.ascii_letters + string.digits
        return ''.join(choices(pool, k=6)).upper()
        
        
    async def _create_room(self, session: ClientSession) -> ResponseProtocol:
        if session.room_id is not None:
            return ResponseProtocol(
                status='error',
                message=f'You are already connected to room {session.room_id}'
            )
        
        while True:
            room_id = self._create_random_code()
            if room_id not in self._rooms.keys():
                break
        
        self._rooms[room_id] = Room(
            id=room_id,
            host=session
        )
        
        return ResponseProtocol(
            status='ok',
            message=asdict(RoomResponseDTO(
                room_id=room_id
            )),
        )
        
        
    async def _join_room(self, session: ClientSession, room_id: str) -> ResponseProtocol:
        if session.room_id is not None:
            return ResponseProtocol(
                status='error',
                message=f'You are already connected to room {session.room_id}'
            )
                    
        room_id = room_id.upper()
        room = self._rooms.get(room_id)
        
        if room is None:
            return ResponseProtocol('error', f'Room {room_id} does not exist.')
        
        return await room.join_room(session)
    
    
    async def _coin_choice(self, session: ClientSession, choice: CoinChoice) -> ResponseProtocol:
        room = self._rooms[session.room_id]
        
        game = room.game
        
        if game is None:
            return ResponseProtocol(
                'error',
                'Game has not started yet'
            )
            
        game.submit_choice(session=session, choice=choice)
        
        return await game.wait_for_result()
    
    
    async def _rematch_requests(self, session: ClientSession, accept: bool) -> ResponseProtocol:
        room = self._rooms[session.room_id]
        
        game = room.game
        
        if game is not None:
            return ResponseProtocol(
                'error',
                'Game is still running'
            )
        
        room.set_rematch_choice(session, accept)
        
        return await room.wait_for_result()
        
        
    async def _handle_message(self, session: ClientSession, message: Any) -> ResponseProtocol:
        message = self._message_adapter.validate_json(message)
                        
        if isinstance(message, CreateRoomProtocol):
            return await self._create_room(session)
            
        elif isinstance(message, JoinRoomProtocol):
            return await self._join_room(session, message.room_id)
        
        elif isinstance(message, CoinChoiceProtocol):
            return await self._coin_choice(session, message.choice)
        
        elif isinstance(message, RematchProtocol):
            return await self._rematch_requests(session, message.accept)
    
        raise RuntimeError(f'Unable to parse recieved message {message}')
    
    
    async def _handle_conn(self, websocket: ServerConnection) -> None:
        session_id = uuid4()
        session = ClientSession(id=session_id, websocket=websocket)
        
        self._sessions[session_id] = session
        
        self._logger.info(f'Client connected {session.websocket.remote_address}')
        
        async for message in session.websocket:
            try:
                response = await self._handle_message(
                    session=session,
                    message=message,
                )
                
                await session.send_message(
                    message=response
                )
                self._logger.info(f'Sent message to {session.websocket.remote_address}: {response}')
                
            except ValidationError as exc:
                await self._send_message(
                    websocket,
                    ResponseProtocol(
                        status='error',
                        message=exc.errors()
                    )
                )   
        
        self._logger.info(f'Client disconnected {websocket.remote_address}')
        
        self._sessions.pop(session.id)

        
    async def run(self):
        self._server = await serve(
            self._handle_conn,
            self._host,
            self._port,
        )

        self._logger.info(f"Server running on ws://{self._host}:{self._port}")
        
        await self._server.serve_forever()
        

