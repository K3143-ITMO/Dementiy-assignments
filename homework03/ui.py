"""
UI superclass definition
"""
import abc

from life import GameOfLife


class UI(abc.ABC):
    """
    ABC wrapping up GameOfLife for UI implementation
    """

    def __init__(self, life: GameOfLife) -> None:
        self.life = life

    @abc.abstractmethod
    def run(self) -> None:
        """
        UI running stub
        """
