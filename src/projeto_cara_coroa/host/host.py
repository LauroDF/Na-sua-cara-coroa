import asyncio

from websockets import server, Server, ServerConnection

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
        self._logger = init_logger()
        
    
    async def handle_conn(self, websocket: ServerConnection) -> None:
        
        self._logger.info(f'Client connected {websocket.remote_address}')
        
        await websocket.wait_closed()
        
        self._logger.info(f'Client disconnected {websocket.remote_address}')
        
        
    