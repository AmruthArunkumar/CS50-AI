"""
Tic Tac Toe Player
"""

import copy
import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    Xnum = 0
    Onum = 0
    for i in range(3):
        for j in range(3):
            if board[i][j] == X:
                Xnum += 1
            if board[i][j] == O:
                Onum += 1
    if Xnum == Onum:
        return X
    if Xnum > Onum:
        return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    moves = []
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                moves.append((i, j))
    return set(moves)


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    ax = action[0]
    ay = action[1]
    board2 = copy.deepcopy(board)
    if board2[ax][ay] != EMPTY:
        raise Exception("Place has to be empty")
    else:
        board2[action[0]][action[1]] = player(board)

    return board2


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    cur = [[[1, 1], [1, 2], [1, 3]],
           [[2, 1], [2, 2], [2, 3]],
           [[3, 1], [3, 2], [3, 3]],
           [[1, 1], [2, 1], [3, 1]],
           [[1, 2], [2, 2], [3, 2]],
           [[1, 3], [2, 3], [3, 3]],
           [[1, 1], [2, 2], [3, 3]],
           [[3, 1], [2, 2], [1, 3]]]

    goals = [[None, None, None],
             [None, None, None],
             [None, None, None],
             [None, None, None],
             [None, None, None],
             [None, None, None],
             [None, None, None],
             [None, None, None]]

    for i in range(3):
        for j in range(3):
            for k in range(8):
                for l in range(3):
                    if (i+1) == cur[k][l][0] and (j+1) == cur[k][l][1]:
                        goals[k][l] = board[i][j]

    for i in range(8):
        if goals[i] == [X, X, X]:
            return X
        if goals[i] == [O, O, O]:
            return O

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    game = winner(board)
    if game == X or game == O:
        return True
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                return False
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    if player(board) == X:
        score = -math.inf
        move = None

        for action in actions(board):
            vmin = min_value(result(board, action))
            if vmin > score:
                score = vmin
                move = action
        return move
    elif player(board) == O:
        score = math.inf
        move = None

        for action in actions(board):
            vmax = max_value(result(board, action))
            if vmax < score:
                score = vmax
                move = action
        return move


def max_value(state):
    v = -math.inf
    if terminal(state):
        return utility(state)
    for action in actions(state):
        v = max(v, min_value(result(state, action)))
    return v


def min_value(state):
    v = math.inf
    if terminal(state):
        return utility(state)
    for action in actions(state):
        v = min(v, max_value(result(state, action)))
    return v

