from typing import get_args
from asyncio import Future, gather
from random import choice

from ..logger import init_logger

from ..client.session import ClientSession

from ..protocols import (
    ResponseProtocol
)

from ..schemas import (
    CoinChoice,
    RoundResult
)


class Game:
    def __init__(self, player_1: ClientSession, player_2: ClientSession):
        self._player_1 = player_1
        self._player_2 = player_2
        
        self._final_score = 5
        
        self._running: bool = False
        self._player_1_score: int = 0
        self._player_2_score: int = 0
        
        self._choice: CoinChoice
        self._logger = init_logger(__name__)
        
        self._player_1_choice: Future[CoinChoice]
        self._player_2_choice: Future[CoinChoice]
        self._round_result: Future[RoundResult]
        
        
    def _set_player_choice(self, player_choice: Future, choice: CoinChoice) -> None:
        if not player_choice.done():
            player_choice.set_result(choice)
    
    
    def _calculate_scores(self, 
        player_1_choice: CoinChoice, 
        player_2_choice: CoinChoice,
    ) -> None:
        options = list(get_args(CoinChoice))
        
        self._choice = choice(options)
        self._logger.info(f'Coin landed on {self._choice}')
        
        if player_1_choice == self._choice:
            self._player_1_score += 1
            
        if player_2_choice == self._choice:
            self._player_2_score += 1
    
    
    def _process_gamestate(self) -> None:
        
        if (
            (
                self._player_1_score >= self._final_score 
                or self._player_2_score >= self._final_score
            ) 
            and abs(self._player_1_score - self._player_2_score) >= 2
        ):
            status = 'game_finish'
            self._running = False
        else:
            status = 'next_round'
        
        self._round_result.set_result(
            RoundResult(
                status=status,
                host_score=self._player_1_score,
                guest_score=self._player_2_score,
                result=self._choice,
            )
        )
        
        self._logger.info(
            f'Result: {self._round_result.result()}'
        )
    
    
    async def wait_for_result(self) -> ResponseProtocol:
        future = self._round_result

        result = await future

        return ResponseProtocol(
            'ok',
            result,
        )
    
        
    async def start(self):
        self._running = True
        
        while self._running:
            self._player_1_choice = Future()
            self._player_2_choice = Future()
            self._round_result = Future()
                    
            choice_1, choice_2 = await gather(
                self._player_1_choice,
                self._player_2_choice,
            )
            
            
            self._calculate_scores(choice_1, choice_2)
            
            self._process_gamestate()
            
        
    
    def submit_choice(self, session: ClientSession, choice: CoinChoice) -> None:
        if session is self._player_1:
            self._logger.info(f'player_1 chose {choice}')
            return self._set_player_choice(self._player_1_choice, choice)
            
        elif session is self._player_2:
            self._logger.info(f'player_2 chose {choice}')
            return self._set_player_choice(self._player_2_choice, choice)
        
        raise RuntimeError(
            f'Session does not belong to this game'
        )