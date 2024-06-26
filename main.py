import random

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"

class Ship:
    def __init__(self, bow, length, orient):
        self.bow = bow
        self.length = length
        self.orient = orient
        self.lives = length

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.orient == 0:  # horizontal
                cur_x += i
            elif self.orient == 1:  # vertical
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))
        return ship_dots

class Board:
    def __init__(self, hid=False):
        self.hid = hid
        self.field = [['O'] * 6 for _ in range(6)]
        self.ships = []
        self.live_ships = 0
        self.busy = []

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = '■'
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)
        self.live_ships += 1

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = '.'
                    self.busy.append(cur)

    def out(self, d):
        return not ((0 <= d.x < 6) and (0 <= d.y < 6))

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()
        if d in self.busy:
            raise BoardUsedException()
        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = 'X'
                if ship.lives == 0:
                    self.live_ships -= 1
                    self.contour(ship, verb=True)
                    print("Ship destroyed!")
                    return False
                else:
                    print("Ship hit!")
                    return True

        self.field[d.x][d.y] = 'T'
        print("Miss!")
        return False

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i+1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "O")
        return res

    def begin(self):
        self.busy = []

class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "You tried to shoot outside the board!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "You've already shot at this cell!"

class BoardWrongShipException(BoardException):
    pass

class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class AI(Player):
    def ask(self):
        d = Dot(random.randint(0, 5), random.randint(0, 5))
        print(f"AI chooses: {d.x + 1} {d.y + 1}")
        return d

class User(Player):
    def ask(self):
        while True:
            cords = input("Your turn: ").split()
            if len(cords) != 2:
                print("Enter 2 coordinates!")
                continue
            x, y = cords
            if not (x.isdigit()) or not (y.isdigit()):
                print("Enter numbers!")
                continue
            x, y = int(x), int(y)
            return Dot(x - 1, y - 1)

class Game:
    def __init__(self):
        self.user_board = self.random_board()
        self.ai_board = self.random_board()
        self.user = User(self.user_board, self.ai_board)
        self.ai = AI(self.ai_board, self.user_board)

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board()
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(random.randint(0, 5), random.randint(0, 5)), l, random.randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        print("Welcome to the game!")
        print("Enter coordinates in the format: x y")
        print("x - row number, y - column number")

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("User board:")
            print(self.user_board)
            print("-" * 20)
            print("AI board:")
            print(self.ai_board)
            if num % 2 == 0:
                print("-" * 20)
                print("User's turn!")
                repeat = self.user.move()
            else:
                print("-" * 20)
                print("AI's turn!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai_board.live_ships == 0:
                print("-" * 20)
                print("User wins!")
                break

            if self.user_board.live_ships == 0:
                print("-" * 20)
                print("AI wins!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()

if __name__ == "__main__":
    game = Game()
    game.start()