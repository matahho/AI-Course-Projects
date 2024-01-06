import random
import time
import turtle
import copy


class OthelloUI:
    def __init__(self, board_size=6, square_size=60):
        self.board_size = board_size
        self.square_size = square_size
        self.screen = turtle.Screen()
        self.screen.setup(self.board_size * self.square_size + 50, self.board_size * self.square_size + 50)
        self.screen.bgcolor('white')
        self.screen.title('Othello')
        self.pen = turtle.Turtle()
        self.pen.hideturtle()
        self.pen.speed(0)
        turtle.tracer(0, 0)


    def draw_board(self, board):
        self.pen.penup()
        x, y = -self.board_size / 2 * self.square_size, self.board_size / 2 * self.square_size
        for i in range(self.board_size):
            self.pen.penup()
            for j in range(self.board_size):
                self.pen.goto(x + j * self.square_size, y - i * self.square_size)
                self.pen.pendown()
                self.pen.fillcolor('green')
                self.pen.begin_fill()
                self.pen.setheading(0)
                for _ in range(4):
                    self.pen.forward(self.square_size)
                    self.pen.right(90)
                self.pen.penup()
                self.pen.end_fill()
                self.pen.goto(x + j * self.square_size + self.square_size / 2,
                              y - i * self.square_size - self.square_size + 5)
                if board[i][j] == 1:
                    self.pen.fillcolor('white')
                    self.pen.begin_fill()
                    self.pen.circle(self.square_size / 2 - 5)
                    self.pen.end_fill()
                elif board[i][j] == -1:
                    self.pen.fillcolor('black')
                    self.pen.begin_fill()
                    self.pen.circle(self.square_size / 2 - 5)
                    self.pen.end_fill()

        turtle.update()


class Othello:
    def __init__(self, ui, minimax_depth=1, prune=True):
        self.size = 6
        self.ui = OthelloUI(self.size) if ui else None
        self.board = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.board[int(self.size / 2) - 1][int(self.size / 2) - 1] = self.board[int(self.size / 2)][
            int(self.size / 2)] = 1
        self.board[int(self.size / 2) - 1][int(self.size / 2)] = self.board[int(self.size / 2)][
            int(self.size / 2) - 1] = -1
        self.current_turn = random.choice([1, -1])
        self.depth = minimax_depth
        self.prune = prune
        self.seenNodes = 0 

    def get_winner(self):
        white_count = sum([row.count(1) for row in self.board])
        black_count = sum([row.count(-1) for row in self.board])
        if white_count > black_count:
            return 1
        elif white_count < black_count:
            return -1
        else:
            return 0

    def get_valid_moves(self, player):
        moves = set()
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 0:
                    for di in [-1, 0, 1]:
                        for dj in [-1, 0, 1]:
                            if di == 0 and dj == 0:
                                continue
                            x, y = i, j
                            captured = []
                            while 0 <= x + di < self.size and 0 <= y + dj < self.size and self.board[x + di][
                                    y + dj] == -player:
                                captured.append((x + di, y + dj))
                                x += di
                                y += dj
                            if 0 <= x + di < self.size and 0 <= y + dj < self.size and self.board[x + di][
                                    y + dj] == player and len(captured) > 0:
                                moves.add((i, j))
        return list(moves)

    def make_move(self, player, move):
        i, j = move
        self.board[i][j] = player
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if di == 0 and dj == 0:
                    continue
                x, y = i, j
                captured = []
                while 0 <= x + di < self.size and 0 <= y + dj < self.size and self.board[x + di][y + dj] == -player:
                    captured.append((x + di, y + dj))
                    x += di
                    y += dj
                if 0 <= x + di < self.size and 0 <= y + dj < self.size and self.board[x + di][y + dj] == player:
                    for (cx, cy) in captured:
                        self.board[cx][cy] = player

    def get_cpu_move(self):
        moves = self.get_valid_moves(-1)
        if len(moves) == 0:
            return None
        return random.choice(moves)


    def comeback (self, prevBoard):
        self.board = prevBoard


    def calc_heuristic (self):
        white_count = sum([row.count(1) for row in self.board])
        black_count = sum([row.count(-1) for row in self.board])
        heuristic = (white_count - black_count) 
        return heuristic
    
    def minimax(self, depth, player, alpha, beta):
        if depth == 0:
            return self.calc_heuristic() , None

        moves = self.get_valid_moves(player)
        if len(moves) == 0:
            if self.get_valid_moves(-player):
                return self.minimax(depth, -player, alpha, beta)[0], None
            else:
                return self.calc_heuristic(), None

        best_move = None
        if player == 1:
            max_eval = float('-inf')
            for move in moves:
                self.seenNodes += 1 
                prevBoard = copy.deepcopy(self.board)
                self.make_move(player, move)
                eval = self.minimax(depth - 1, -player, alpha, beta)[0]
                self.comeback(prevBoard)
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, max_eval)
                if self.prune and beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in moves:
                self.seenNodes += 1 
                prevBoard = copy.deepcopy(self.board)
                self.make_move(player, move)
                eval = self.minimax(depth - 1, -player, alpha, beta)[0]
                self.comeback(prevBoard)
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, min_eval)
                if self.prune and beta <= alpha:
                    break
            return min_eval, best_move

    def get_human_move(self):
        return self.minimax(self.depth, 1, float('-inf'), float('inf'))[1]
        

    def terminal_test(self):
        return len(self.get_valid_moves(1)) == 0 and len(self.get_valid_moves(-1)) == 0

    def play(self):
        winner = None
        while not self.terminal_test():
            if self.ui:
                self.ui.draw_board(self.board)
            if self.current_turn == 1:
                move = self.get_human_move()
                if move:
                    self.make_move(self.current_turn, move)
            else:
                move = self.get_cpu_move()
                if move:
                    self.make_move(self.current_turn, move)
            self.current_turn = -self.current_turn
            if self.ui:
                self.ui.draw_board(self.board)
                time.sleep(1)
        winner = self.get_winner()
        return winner



def printResult (Runs , times , seenNodes , wins , depth ):
    print ("depth of search : " , depth)
    print ("Number of plays : " , Runs)
    print ("Mean running duration : " ,  round ((times/Runs),6) , "s")
    print ("Mean of Seen Nodes is : " , (seenNodes/Runs) , "nodes")
    print ("AI win probability : " , (wins/Runs))
    

if __name__=="__main__":
    whiteWins = 0 
    times = 0 
    seenNodes = 0 
    numberOfRuns = 10
    for i in range(numberOfRuns):
        tic = time.time()
        oth = Othello(1, minimax_depth=7, prune=True)
        winner = oth.play()
        toc = time.time()
        seenNodes += oth.seenNodes
        times += round((toc - tic), 6)
        if winner == 1 :
            whiteWins += 1 
    printResult(numberOfRuns , times , seenNodes , whiteWins , oth.depth)