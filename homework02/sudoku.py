import multiprocessing
import pathlib
import random
import time
import typing as tp

random.seed(time)  # init PRNG

T = tp.TypeVar("T")


def read_sudoku(path: tp.Union[str, pathlib.Path]) -> tp.List[tp.List[str]]:
    """ Прочитать Судоку из указанного файла """
    path = pathlib.Path(path)
    with path.open() as f:
        puzzle = f.read()
    return create_grid(puzzle)


def create_grid(puzzle: str) -> tp.List[tp.List[str]]:
    digits = [c for c in puzzle if c in "123456789."]
    grid = group(digits, 9)
    return grid


def display(grid: tp.List[tp.List[str]]) -> None:
    """Вывод Судоку """
    width = 2
    line = "+".join(["-" * (width * 3)] * 3)
    for row in range(9):
        print(
            "".join(
                grid[row][col].center(width) + ("|" if str(col) in "25" else "") for col in range(9)
            )
        )
        if str(row) in "25":
            print(line)
    print()


def group(values: tp.List[T], n: int) -> tp.List[tp.List[T]]:
    """
    Сгруппировать значения values в список, состоящий из списков по n элементов

    >>> group([1,2,3,4], 2)
    [[1, 2], [3, 4]]
    >>> group([1,2,3,4,5,6,7,8,9], 3)
    [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    """
    return [values[i : i + n] for i in range(0, len(values), n)]


def get_row(grid: tp.List[tp.List[str]], pos: tp.Tuple[int, int]) -> tp.List[str]:
    """Возвращает все значения для номера строки, указанной в pos

    >>> get_row([['1', '2', '.'], ['4', '5', '6'], ['7', '8', '9']], (0, 0))
    ['1', '2', '.']
    >>> get_row([['1', '2', '3'], ['4', '.', '6'], ['7', '8', '9']], (1, 0))
    ['4', '.', '6']
    >>> get_row([['1', '2', '3'], ['4', '5', '6'], ['.', '8', '9']], (2, 0))
    ['.', '8', '9']
    """
    return grid[pos[0]]  # 0 is the row coordinate index


def get_col(grid: tp.List[tp.List[str]], pos: tp.Tuple[int, int]) -> tp.List[str]:
    """Возвращает все значения для номера столбца, указанного в pos

    >>> get_col([['1', '2', '.'], ['4', '5', '6'], ['7', '8', '9']], (0, 0))
    ['1', '4', '7']
    >>> get_col([['1', '2', '3'], ['4', '.', '6'], ['7', '8', '9']], (0, 1))
    ['2', '.', '8']
    >>> get_col([['1', '2', '3'], ['4', '5', '6'], ['.', '8', '9']], (0, 2))
    ['3', '6', '9']
    """
    return [grid[i][pos[1]] for i in range(len(grid))]  # 1 is the column coordinate index


def get_block(grid: tp.List[tp.List[str]], pos: tp.Tuple[int, int]) -> tp.List[str]:
    """Возвращает все значения из квадрата, в который попадает позиция pos

    >>> grid = read_sudoku('puzzle1.txt')
    >>> get_block(grid, (0, 1))
    ['5', '3', '.', '6', '.', '.', '.', '9', '8']
    >>> get_block(grid, (4, 7))
    ['.', '.', '3', '.', '.', '1', '.', '.', '6']
    >>> get_block(grid, (8, 8))
    ['2', '8', '.', '.', '.', '5', '.', '7', '9']
    """
    block_start_x = pos[0] - pos[0] % 3  # block starts at 0, 3, or 6
    block_start_y = pos[1] - pos[1] % 3  # block starts at 0, 3, or 6
    block = [
        [
            grid[block_start_x + i][block_start_y + j] for j in range(3)
        ]  # gets us "chunks" of 3 rows that make up a blocks
        for i in range(3)
    ]
    return [j for i in block for j in i]


def find_empty_positions(grid: tp.List[tp.List[str]]) -> tp.Optional[tp.Tuple[int, int]]:
    """Найти первую свободную позицию в пазле

    >>> find_empty_positions([['1', '2', '.'], ['4', '5', '6'], ['7', '8', '9']])
    (0, 2)
    >>> find_empty_positions([['1', '2', '3'], ['4', '.', '6'], ['7', '8', '9']])
    (1, 1)
    >>> find_empty_positions([['1', '2', '3'], ['4', '5', '6'], ['.', '8', '9']])
    (2, 0)
    """
    empty_positions = [
        [(i, j) for j in range(len(grid[i])) if grid[i][j] == "."] for i in range(len(grid))
    ]
    # this creates a list consisting of lists, each holding the positions of the dot symbols in the corresponding sublists of grid (as tuples)
    # if the original sublist contains no dots, the corresponding list in empty_positions is empty
    flattened_empty_positions = [j for i in empty_positions for j in i]  # flatten
    # Flattening removes the empty lists, compressing empty_positions and leaving a list of tuples
    if len(flattened_empty_positions) == 0:
        return None  # no position found
    return flattened_empty_positions[0]  # get first tuple, i. e, first dots' position


def find_possible_values(grid: tp.List[tp.List[str]], pos: tp.Tuple[int, int]) -> tp.Set[str]:
    """Вернуть множество возможных значения для указанной позиции

    >>> grid = read_sudoku('puzzle1.txt')
    >>> values = find_possible_values(grid, (0,2))
    >>> values == {'1', '2', '4'}
    True
    >>> values = find_possible_values(grid, (4,7))
    >>> values == {'2', '5', '9'}
    True
    """
    return set(
        [
            str(i)  # explicit cast required since we use strings for values in grid
            for i in range(1, 10)
            if not str(i) in get_col(grid, pos)
            and not str(i) in get_row(grid, pos)
            and not str(i) in get_block(grid, pos)
        ]
    )


def solve(grid: tp.List[tp.List[str]]) -> tp.Optional[tp.List[tp.List[str]]]:
    """ Решение пазла, заданного в grid """
    """ Как решать Судоку?
        1. Найти свободную позицию
        2. Найти все возможные значения, которые могут находиться на этой позиции
        3. Для каждого возможного значения:
            3.1. Поместить это значение на эту позицию
            3.2. Продолжить решать оставшуюся часть пазла

    >>> grid = read_sudoku('puzzle1.txt')
    >>> solve(grid)
    [['5', '3', '4', '6', '7', '8', '9', '1', '2'], ['6', '7', '2', '1', '9', '5', '3', '4', '8'], ['1', '9', '8', '3', '4', '2', '5', '6', '7'], ['8', '5', '9', '7', '6', '1', '4', '2', '3'], ['4', '2', '6', '8', '5', '3', '7', '9', '1'], ['7', '1', '3', '9', '2', '4', '8', '5', '6'], ['9', '6', '1', '5', '3', '7', '2', '8', '4'], ['2', '8', '7', '4', '1', '9', '6', '3', '5'], ['3', '4', '5', '2', '8', '6', '1', '7', '9']]
    """
    empty_pos = find_empty_positions(grid)
    if not empty_pos:
        return grid  # we should be done already!
    else:
        possible_vals = find_possible_values(grid, empty_pos)
        if possible_vals:
            for i in possible_vals:
                grid[empty_pos[0]][empty_pos[1]] = i
                if solve(grid):  # we can return None, if solving the current one fails
                    return solve(grid)  # try next pos
        grid[empty_pos[0]][empty_pos[1]] = "."  # backtrack

    return None  # no solution found, we have fehled the emprah


def check_solution(solution: tp.List[tp.List[str]]) -> bool:
    """ Если решение solution верно, то вернуть True, в противном случае False """
    # TODO: Add doctests with bad puzzles
    if not solution:  # impossible to solve, lol
        return False
    if find_empty_positions(solution):  # do not accept incomplete grids
        return False
    for i in range(1, 10):  # 1, 2, 3 ... 9 (digits)
        for j in range(1, 10):  # consistency matters
            # (i/j - 1) will be 0, 1, 2, .. 8 (indices)
            col = get_col(solution, (i - 1, j - 1))
            row = get_row(solution, (i - 1, j - 1))
            block = get_block(solution, (i - 1, j - 1))
            if (
                not col.count(str(i)) == 1
                or not row.count(str(i)) == 1
                or not block.count(str(i)) == 1
            ):  # see sudoku rules
                # explicit casts to str required
                return False
    return True


def generate_sudoku(N: int) -> tp.List[tp.List[str]]:
    """Генерация судоку заполненного на N элементов

    >>> grid = generate_sudoku(40)
    >>> sum(1 for row in grid for e in row if e == '.')
    41
    >>> solution = solve(grid)
    >>> check_solution(solution)
    True
    >>> grid = generate_sudoku(1000)
    >>> sum(1 for row in grid for e in row if e == '.')
    0
    >>> solution = solve(grid)
    >>> check_solution(solution)
    True
    >>> grid = generate_sudoku(0)
    >>> sum(1 for row in grid for e in row if e == '.')
    81
    >>> solution = solve(grid)
    >>> check_solution(solution)
    True
    """
    grid = [["." for j in range(9)] for i in range(9)]  # generate empty grid
    grid_solved = solve(grid)  # fill with some numbers
    if not grid_solved:
        return grid  # should never be
    if N > 81:  # too many numbers
        return grid  # should be solved already
    while not sum(1 for row in grid for e in row if e == ".") == 81 - N:  # see docstring
        # delete some values from the solved puzzle
        pos = (random.randint(0, 8), random.randint(0, 8))  # select random cell
        if grid[pos[0]][pos[1]] == ".":  # empty already
            continue
        grid[pos[0]][pos[1]] = "."

    return grid


def run_solve(filename: str) -> None:
    grid = read_sudoku(filename)
    start = time.time()
    solve(grid)
    end = time.time()
    print(f"{filename}: {end-start}")


if __name__ == "__main__":
    for filename in ["puzzle1.txt", "puzzle2.txt", "puzzle3.txt"]:
        p = multiprocessing.Process(
            target=run_solve, args=(filename,)
        )  # spawn separate processes to avoid GIL
        p.start()
