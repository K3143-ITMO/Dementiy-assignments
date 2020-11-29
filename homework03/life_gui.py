"""
Conway's Game Of Life, GUI version
"""
# pylint: disable=no-member
import pathlib

import life
import pygame
from life import GameOfLife
from ui import UI


class GUI(UI):
    """
    UI subclass implementing GUI
    """

    def __init__(self, game: GameOfLife, cell_size: int = 10, speed: int = 10) -> None:
        super().__init__(game)

        self.width = self.life.cols * cell_size
        self.height = self.life.rows * cell_size
        self.cell_size = cell_size

        self.screen = pygame.display.set_mode((self.width, self.height))  # create screen
        self.speed = speed

    def draw_lines(self) -> None:
        """
        Draw lines marking cell borders
        """
        for x_c in range(0, self.width, self.cell_size):
            pygame.draw.line(self.screen, pygame.Color("black"), (x_c, 0), (x_c, self.height))
        for y_c in range(0, self.height, self.cell_size):
            pygame.draw.line(self.screen, pygame.Color("black"), (0, y_c), (self.width, y_c))

    def draw_grid(self) -> None:
        """
        Draw cell contents
        """
        for i in range(len(self.life.curr_generation)):
            for j in range(len(self.life.curr_generation[i])):
                cell_color = (
                    pygame.Color("green") if self.life.is_alive((i, j)) else pygame.Color("white")
                )
                rect = pygame.Rect(
                    self.cell_size * j, self.cell_size * i, self.cell_size, self.cell_size
                )
                pygame.draw.rect(self.screen, cell_color, rect)

    def flip_cell_state(self, cell: life.Cell) -> None:
        """
        Change cell state from "dead" to "alive" and vice versa
        """
        cell_x = cell[0] // self.cell_size
        cell_y = cell[1] // self.cell_size
        if self.life.is_alive((cell_x, cell_y)):
            self.life.set_cell_value((cell_x, cell_y), 0)
        else:  # can't be anything else
            self.life.set_cell_value((cell_x, cell_y), 1)

    def run(self) -> None:
        pygame.init()
        clock = pygame.time.Clock()
        pygame.display.set_caption("Game of Life")
        self.screen.fill(pygame.Color("white"))

        self.life.curr_generation = self.life.create_grid(randomize=True)

        running = True
        pause = False
        while running:
            self.draw_grid()
            self.draw_lines()
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    (
                        y_c,
                        x_c,
                    ) = (
                        pygame.mouse.get_pos()
                    )  # inverted due to graphics having a weird coordinate system
                    self.flip_cell_state((x_c, y_c))
                    self.draw_grid()
                    self.draw_lines()
                    pygame.display.flip()
                    clock.tick(self.speed)
                    continue
                elif event.type == pygame.KEYDOWN:  # get event
                    if event.key == pygame.K_PAUSE:  # check pause key
                        if pause:
                            pause = False
                        else:
                            pause = True
                    if event.key == pygame.K_s:  # check save key
                        self.life.save(pathlib.Path("save.txt"))
                    if event.key == pygame.K_l:  # check load key
                        self.life.from_file(pathlib.Path("save.txt"))

            if pause:  # actually pause the game
                continue

            # Выполнение одного шага игры (обновление состояния ячеек)
            if self.life.is_changing and not self.life.is_max_generations_exceeded:
                self.life.step()
                pygame.display.flip()
            else:
                running = False

            clock.tick(self.speed)
        pygame.quit()


if __name__ == "__main__":
    args = life.get_args()
    game_instance = GameOfLife(
        (args.width // args.cell_size, args.height // args.cell_size), max_generations=args.max_gens
    )
    if args.load_path:
        game_instance = game_instance.from_file(args.load_path)
    app = GUI(game_instance, cell_size=args.cell_size)
    app.run()
