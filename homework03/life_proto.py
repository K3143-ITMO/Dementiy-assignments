"""
Conway's Game Of Life prototype
"""
# pylint: disable=no-member
import random
import typing as tp
from copy import deepcopy

import pygame

Cell = tp.Tuple[int, int]
Cells = tp.List[int]
Grid = tp.List[Cells]


class GameOfLife:
    """
    Business logic class
    """

    def __init__(
        self, width: int = 640, height: int = 480, cell_size: int = 10, speed: int = 10
    ) -> None:
        self.width = width
        self.height = height
        self.cell_size = cell_size

        # Устанавливаем размер окна
        self.screen_size = width, height
        # Создание нового окна
        self.screen = pygame.display.set_mode(self.screen_size)

        # Вычисляем количество ячеек по вертикали и горизонтали
        self.cell_width = self.width // self.cell_size
        self.cell_height = self.height // self.cell_size

        # Скорость протекания игры
        self.speed = speed

        self.grid = self.create_grid()

    def draw_lines(self) -> None:
        """ Отрисовать сетку """
        for x_c in range(0, self.width, self.cell_size):
            pygame.draw.line(self.screen, pygame.Color("black"), (x_c, 0), (x_c, self.height))
        for y_c in range(0, self.height, self.cell_size):
            pygame.draw.line(self.screen, pygame.Color("black"), (0, y_c), (self.width, y_c))

    def run(self) -> None:
        """ Запустить игру """
        pygame.init()
        clock = pygame.time.Clock()
        pygame.display.set_caption("Game of Life")
        self.screen.fill(pygame.Color("white"))

        self.grid = self.create_grid(randomize=True)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.draw_grid()
            self.draw_lines()

            # Выполнение одного шага игры (обновление состояния ячеек)
            self.grid = self.get_next_generation()

            pygame.display.flip()
            clock.tick(self.speed)
        pygame.quit()

    def is_alive(self, cell: Cell) -> bool:
        """
        Checks if a cell is alive
        """
        return bool(self.grid[cell[0]][cell[1]])

    def _is_a_cell(self, cell: Cell) -> bool:
        """
        Checks a cell for coordinate validity
        """
        return 0 <= cell[0] < len(self.grid) and 0 <= cell[1] < len(self.grid[0])

    def create_grid(self, randomize: bool = False) -> Grid:
        """
        Создание списка клеток.

        Клетка считается живой, если ее значение равно 1, в противном случае клетка
        считается мертвой, то есть, ее значение равно 0.

        Parameters
        ----------
        randomize : bool
            Если значение истина, то создается матрица, где каждая клетка может
            быть равновероятно живой или мертвой, иначе все клетки создаются мертвыми.

        Returns
        ----------
        out : Grid
            Матрица клеток размером `cell_height` х `cell_width`.
        """
        return [
            [random.randint(0, 1) if randomize else 0 for _ in range(self.cell_width)]
            for _ in range(self.cell_height)
        ]

    def draw_grid(self) -> None:
        """
        Отрисовка списка клеток с закрашиванием их в соответствующе цвета.
        """
        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                cell_color = (
                    pygame.Color("green") if self.is_alive((i, j)) else pygame.Color("white")
                )
                rect = pygame.Rect(
                    self.cell_size * j, self.cell_size * i, self.cell_size, self.cell_size
                )
                pygame.draw.rect(self.screen, cell_color, rect)

    def get_neighbours(self, cell: Cell) -> Cells:
        """
        Вернуть список соседних клеток для клетки `cell`.

        Соседними считаются клетки по горизонтали, вертикали и диагоналям,
        то есть, во всех направлениях.

        Parameters
        ----------
        cell : Cell
            Клетка, для которой необходимо получить список соседей. Клетка
            представлена кортежем, содержащим ее координаты на игровом поле.

        Returns
        ----------
        out : Cells
            Список соседних клеток.
        """
        neighbors = []
        shifts = ((i, j) for i in [-1, 0, 1] for j in [-1, 0, 1])  # possible shifts for neighbors
        for x_c, y_c in shifts:  # 9 possible cells in a quadrant
            if (x_c, y_c) == (0, 0):  # except the one we check
                continue

            row, col = cell[0] + x_c, cell[1] + y_c
            if self._is_a_cell((row, col)):
                neighbors.append(int(self.is_alive((row, col))))

        return neighbors

    def get_next_generation(self) -> Grid:
        """
        Получить следующее поколение клеток.

        Returns
        ----------
        out : Grid
            Новое поколение клеток.
        """
        out = deepcopy(
            self.grid
        )  # because python assignments create references and do not copy values
        # https://docs.python.org/3/faq/programming.html#how-do-i-copy-an-object-in-python

        for i in range(len(self.grid)):
            for j in range(len(self.grid[i])):
                neighbors = self.get_neighbours((i, j))
                alive = sum(neighbors)

                if self.is_alive((i, j)):
                    if 2 <= alive <= 3:  # supports life
                        out[i][j] = 1
                    else:  # either no food or overpopulated
                        out[i][j] = 0
                elif alive == 3:  # breathe life into a dead cell near some alive cells
                    out[i][j] = 1

        return out


if __name__ == "__main__":
    game = GameOfLife(320, 240, 20)
    game.run()
