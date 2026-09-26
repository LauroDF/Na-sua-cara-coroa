import asyncio
from dataclasses import asdict

from ..client.session import ClientSession

from .game import Game

from ..logger import init_logger

from ..schemas import (
    RoomResponseDTO,
    RematchResponse,
)

from ..protocols import (
    ResponseProtocol,
)


class Room:

    def __init__(
        self,
        id: str,
        host: ClientSession,
    ) -> None:
        self._id = id
        self._host = host
        self._logger = init_logger(__name__)

        self._guest: ClientSession | None = None

        self._game: Game | None = None
        self._game_task: asyncio.Task[None] | None = None
        self._room_task: asyncio.Task[None] | None = None

        self._host_rematch: asyncio.Future[bool]
        self._guest_rematch: asyncio.Future[bool]
        self._rematch_response: asyncio.Future[RematchResponse]

        self._host.connect_to_room(self._id)
        
        
    async def _wait_for_choice( self, future: asyncio.Future[bool]) -> bool:
        return await future
        

    def _initialize_game(self) -> None:
        self._game = Game(
            self._host,
            self._guest,
        )

        self._game_task = asyncio.create_task(
            self._game.start()
        )

        self._logger.info("Game started")

    async def _run(self) -> None:
        while True:
            self._initialize_game()

            await self._game_task

            self._logger.info("Game finished")

            self._game = None
            self._game_task = None

            self._host_rematch = asyncio.Future()
            self._guest_rematch = asyncio.Future()
            self._rematch_response = asyncio.Future()
            
            async with asyncio.TaskGroup() as tg:
                player_1_task = tg.create_task(
                    self._wait_for_choice(self._host_rematch)
                )

                player_2_task = tg.create_task(
                    self._wait_for_choice(self._guest_rematch)
                )

            host_choice = player_1_task.result()
            guest_choice = player_2_task.result()

            if not (host_choice and guest_choice):
                self._rematch_response.set_result(RematchResponse('declined'))
                self._logger.info("Rematch declined")
                
                self._host.disconnect_from_room()
                self._guest.disconnect_from_room()
                break

            self._logger.info("Starting rematch")
            self._rematch_response.set_result(RematchResponse('accepted'))
            
    
    async def wait_for_result(self) -> ResponseProtocol:
        future = self._rematch_response

        result = await future

        return ResponseProtocol(
            'ok',
            result,
        )        
    

    def set_rematch_choice(
        self,
        session: ClientSession,
        choice: bool,
    ) -> None:
        if session is self._host:
            if not self._host_rematch.done():
                self._host_rematch.set_result(choice)

        elif session is self._guest:
            if not self._guest_rematch.done():
                self._guest_rematch.set_result(choice)

        else:
            raise RuntimeError(
                "Session not connected to room"
            )

    async def join_room(
        self,
        guest: ClientSession,
    ) -> ResponseProtocol:
        if self._guest is not None:
            return ResponseProtocol(
                status="error",
                message=f"Room {self._id} is already full."
            )

        self._guest = guest
        self._guest.connect_to_room(self._id)

        self._room_task = asyncio.create_task(
            self._run()
        )

        await self._host.send_message(
            ResponseProtocol(
                status="ok",
                message={
                    "status": "room_ready",
                    "room_id": self._id,
                },
            )
        )

        return ResponseProtocol(
            status="ok",
            message=asdict(
                RoomResponseDTO(
                    room_id=self._id
                )
            )
        )

    @property
    def game(self) -> Game | None:
        return self._game