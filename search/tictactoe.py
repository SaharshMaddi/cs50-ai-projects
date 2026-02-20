"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY], #structure is list of list, somewhat like a 2d arr
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    o_count = 0
    x_count = 0
    for i in board:
        for j in i:
            if j == X:
                x_count+=1
            elif j == O:
                o_count+=1

    # 0 - 0 x goes
    # 1- 0 o goes x>o return o
    return X if x_count == o_count else O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    a = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                a.add((i, j)) # coords
    return a



def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    #must be inside the board
    board1 = copy.deepcopy(board)
    x, y = action
    if x < 0 or x > 2 or y < 0 or y > 2:
        raise Exception("Move is outside the board boundaries.")
    if board1[x][y] != EMPTY:
        raise Exception("Not a valid move buddy")
    else:
        current_player = player(board1)
        board1[x][y] = current_player
        return board1



def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    #this ones kind of hard
    # ways to win: 3 columns, 3 rows, 2 diagonals
    # cols and rows are ez
    # diags need to be hard coded
    for i in range(3):
        #cols first
        if board[i][0] == board[i][1] == board[i][2] == X:
            return X
        if board[i][0] == board[i][1] == board[i][2] == O:
            return O
        #rows
        if board[0][i] == board[1][i] == board[2][i] == X:
            return X
        if board[0][i] == board[1][i] == board[2][i] == O:
            return O
    #top left to bottom right
    if board[0][0] == board[1][1] == board[2][2] == X:
        return X
    if board[0][0] == board[1][1] == board[2][2] == O:
        return O
    if board[0][2] == board[1][1] == board[2][0] == X:
        return X
    if board[0][2] == board[1][1] == board[2][0] == O:
        return O
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    #so basically if there is a winner, then true, else if there isnt any more spots, then over
    num_empty = 0
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                num_empty +=1
    if num_empty == 0:
        return True
    else:
        return True if winner(board) != None else False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    # as far as i can tell, this is by far the hardest function, harder than winner
    #check player to see min or max
    if terminal(board):
        return None
    max_player = True
    current_player = player(board)
    max_player = (current_player == X)
    best_move = None
    if max_player:
        best_v = float("-inf")
        for action in actions(board):
            move_value = minvalue(result(board, action), float("-inf"), float("inf"))
            if move_value > best_v:
                best_v = move_value
                best_move = action
    else:
        best_v = float("inf")
        for action in actions(board):
            move_value = maxvalue(result(board, action), float("-inf"), float("inf"))
            if move_value < best_v:
                best_v = move_value
                best_move = action

    return best_move




def maxvalue(board, alpha, beta):
    if terminal(board):
        return utility(board)
    v = float("-inf")
    for action in actions(board):
        v = max(v, minvalue(result(board, action), alpha, beta))
        alpha = max(alpha, v)
        if alpha >= beta:
            break
    return v

def minvalue(board, alpha, beta):
    if terminal(board):
        return utility(board)
    v = float("inf")
    for action in actions(board):
        v = min(v, maxvalue(result(board, action), alpha, beta))
        beta = min(beta, v)
        if alpha >= beta:
            break
    return v
