import asyncio

from websockets import serve, Server, ServerConnection

from ..logger import init_logger


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
        
    
    async def _handle_conn(self, websocket: ServerConnection) -> None:
        
        self._logger.info(f'Client connected {websocket.remote_address}')
        
        await websocket.wait_closed()
        
        self._logger.info(f'Client disconnected {websocket.remote_address}')
        
        
    async def run(self):
        self.server = await serve(
            self._handle_conn,
            self._host,
            self._port,
        )

        self._logger.info(f"Server running on ws://{self._host}:{self._port}")
        
        await self.server.serve_forever()
        
