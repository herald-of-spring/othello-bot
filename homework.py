# This bot plays Othello on a 12x12 board with [O] starting on c4, d3, i10, j9; [X] starting on c3, d4, i9, j10;
# [O] moves first and [X] gets +1 tiebreaker point
# Special thanks to Professor Imre Leader for providing insight and strategy into this modified version of Othello
# This does not perform input sanitization (as it was not the focus of the project)!
# Instructions: run calibrate.py -> homework.py, which accepts input.txt in the format of player side "X" or "O"
# followed by time left (on a new line) and the 12x12 board (each row also on a new line) with X, O, and . [empty tiles]

import random
from copy import deepcopy
import heapq
from collections import deque


class Board:
    def __init__(self, side, state):
        self.side = side
        self.state = state
        # player valid moves, format [(x,y), [(x1,y1),(x2,y2)...]] i.e. move at (x,y) flips discs (x1,y1)...
        self.pmoves = []
        # opponent valid moves
        self.omoves = 0
        # player disc count
        self.pcount = 0
        # opponent disc count
        self.ocount = 0
        # player center disc count
        self.pcenter = 0
        # opponent center disc count
        self.ocenter = 0
        # player groups
        self.pgroup = 0
        # opponent groups
        self.ogroup = 0
        self.scan_board()
        self.heuristic, self.isLeaf = self.heuristics()

    def scan_board(self):
        visited = [[0 for _ in range(12)] for _ in range(12)]
        for i in range(12):
            for j in range(12):
                if visited[i][j]:
                    continue
                if self.state[i][j] == '.':
                    self.check_move(i, j)
                    visited[i][j] = 1
                else:
                    count, center = self.count_group(self.state[i][j], i, j, visited)
                    if self.state[i][j] == self.side:
                        self.pcount += count
                        self.pcenter += center
                        self.pgroup += 1
                    else:
                        self.ocount += count
                        self.ocenter += center
                        self.ogroup += 1

    # checks if valid move
    def check_move(self, startx, starty):
        # transformations to the 8 surrounding tiles
        dx = [-1, 0, 1, -1, 1, -1, 0, 1]
        dy = [1, 1, 1, 0, 0, -1, -1, -1]
        # flag to avoid duplicate counting of opponent's moves
        flag = 0
        for i in range(8):
            curx = startx + dx[i]
            cury = starty + dy[i]
            side = '.'
            while 0 <= curx < 12 and 0 <= cury < 12:
                # hits empty tile, either right away or after a line of only 1 color, invalid move
                if self.state[curx][cury] == '.':
                    break
                # hits occupied tile the first time
                elif side == '.':
                    side = self.state[curx][cury]
                    # opponent move already counted in previous iteration
                    if flag and self.side == side:
                        break
                # hits occupied tile that does not match the first tile hit (else move on)
                elif self.state[curx][cury] != side:
                    # valid move for opponent
                    if self.side == side:
                        self.omoves += 1
                        flag = 1
                    # valid move for player, calculate affected discs if this move was made
                    else:
                        # new move (flag equivalent to avoid duplicate counting of player's moves)
                        if not self.pmoves or self.pmoves[-1][0] != (startx, starty):
                            self.pmoves.append([(startx, starty), []])
                        while curx - dx[i] != startx or cury - dy[i] != starty:
                            self.pmoves[-1][1].append((curx - dx[i], cury - dy[i]))
                            curx -= dx[i]
                            cury -= dy[i]
                    break
                curx += dx[i]
                cury += dy[i]

    # bfs to scan complete group
    def count_group(self, side, startx, starty, visited):
        dx = [-1, 0, 1, -1, 1, -1, 0, 1]
        dy = [1, 1, 1, 0, 0, -1, -1, -1]
        queue = deque([(startx, starty)])
        count = 0
        center = 0
        visited[startx][starty] = 1
        while queue:
            curx, cury = queue.popleft()
            count += 1
            if 1 < curx < 10 and 1 < cury < 10:
                center += 1
            for i in range(8):
                if 0 <= curx + dx[i] < 12 and 0 <= cury + dy[i] < 12 and \
                        not visited[curx + dx[i]][cury + dy[i]] and self.state[curx + dx[i]][cury + dy[i]] == side:
                    queue.append((curx + dx[i], cury + dy[i]))
                    visited[curx + dx[i]][cury + dy[i]] = 1
        return count, center

    # player corners - opponent corners
    def corner_heuristic(self):
        result = 0
        if self.state[0][0] != '.':
            result += 1 if self.state[0][0] == self.side else -1
        if self.state[0][11] != '.':
            result += 1 if self.state[0][11] == self.side else -1
        if self.state[11][0] != '.':
            result += 1 if self.state[11][0] == self.side else -1
        if self.state[11][11] != '.':
            result += 1 if self.state[11][11] == self.side else -1
        return result

    # player's moves - opponent's moves
    def mobility_heuristic(self):
        return (len(self.pmoves) - self.omoves) / (len(self.pmoves) + self.omoves) \
            if len(self.pmoves) + self.omoves != 0 else 0

    # player's disc count - opponent's disc count, including tiebreaker
    def disc_heuristic(self):
        return (self.pcount - self.ocount + (1 if self.side == 'X' else -1)) / (self.pcount + self.ocount)

    # player's disc count in central 64 tiles - opponent's disc count in central 64 tiles
    def center_control_heuristic(self):
        return (self.pcenter - self.ocenter) / (self.pcenter + self.ocenter)

    # player's separated groups (including diagonals) - opponent's separated groups
    def group_heuristic(self):
        return (max(self.pgroup, 2) - max(self.ogroup, 2)) / (max(self.pgroup, 2) + max(self.ogroup, 2))

    # could add stability heuristic but harder to implement due to wedges etc.
    def heuristics(self):
        # game end condition
        if len(self.pmoves) == 0 and self.omoves == 0:
            return (1e6 if self.disc_heuristic() > 0 else -1e6), True
        elif self.pcount == 0:
            return -1e6, True
        elif self.ocount == 0:
            return 1e6, True
        # metric to measure early/mid/late game by how many discs on the board
        tcount = self.pcount + self.ocount
        # informed heuristics after tournament training - see round-robin-log.txt
        return (0.185 * tcount + 55.6) * self.corner_heuristic() + \
               (0.75 * tcount + 25) * self.mobility_heuristic() + \
               (0.04 * tcount + 9.1) * self.disc_heuristic() + \
               (-0.55 * tcount - 15) * self.center_control_heuristic() + \
               (-0.68 * tcount - 13.6) * self.group_heuristic(), False


# holds state tree to perform alpha beta pruning, incomplete since it takes shortcuts (patience value) for optimization
# alpha beta values ALWAYS from the perspective of the player
class FutureState:
    def __init__(self, b, d, p, pm, alpha, beta):
        self.board = b
        self.depth = d
        self.prev = p
        # what move brought us here
        self.prev_move = pm
        self.next = []
        self.alpha = alpha
        self.beta = beta
        # carry best value heuristic after search back to root
        self.best_val = None
        self.best_move = None
        # number of consecutive prunes before the rest of the nodes are abandoned entirely
        # i.e. assumes the rest of the moves are bad, since original list of moves are ordered
        self.patience = 3

    # generates next layer of states, and orders them in order of most to least favorable (estimate)
    # min-heap since HEURISTICS are INVERTED for opponent; i.e. best outcome for player is worst outcome for opponent
    def generate_ply(self):
        switch_sides = "O" if self.board.side == "X" else "X"
        # no moves for current player, switch sides but do not decrement depth
        if not self.board.pmoves and not self.board.isLeaf:
            obj = FutureState(Board(switch_sides, deepcopy(self.board.state)),
                              self.depth, self, None, self.alpha, self.beta)
            self.next = [(obj.board.heuristic, None, obj)]
        else:
            # generate board if move was played
            for moveset in self.board.pmoves:
                move = moveset[0]
                changes = moveset[1]
                new_board = deepcopy(self.board.state)
                new_board[move[0]][move[1]] = self.board.side
                for c in changes:
                    new_board[c[0]][c[1]] = self.board.side
                obj = FutureState(Board(switch_sides, new_board), self.depth - 1, self, move, self.alpha, self.beta)
                self.next.append((obj.board.heuristic, move, obj))
        # optimization to order most (estimated) appealing moves first, before actually calculating their appeal
        heapq.heapify(self.next)
        self.best_move = self.next[0][1]
        if self.depth == 1:
            self.next = [heapq.heappop(self.next)]
            heapq.heapify(self.next)

    # getter function for the less intuitive heap method, returns (heuristic_value, FutureState object)
    # carries updated alpha beta values down to subsequent nodes
    def get_next(self):
        h, m, updated = heapq.heappop(self.next)
        updated.alpha, updated.beta = self.alpha, self.beta
        return h, updated


# takes board object (carrying state, heuristic, and player information) and how much depth to search
def alpha_beta_minimax(state, ply_depth, ceiling):
    # very low time, cannot think, or if only 1 move
    if not ply_depth or len(state.pmoves) == 1:
        return state.pmoves[0][0]
    # alpha = -100000000 | beta = 100000000
    root = FutureState(state, ply_depth * 2, None, None, -1e9, 1e9)
    curnode = (state.heuristic, root)
    expanded = 0
    # recursion ineffective, (modified) dfs instead
    while curnode[1] and expanded < ceiling:
        est_heuristic, curstate = curnode
        # check suitable depth reached or end game state
        if not curstate.depth or curstate.board.isLeaf:
            # current node is player side -> parent node is opponent side (saves time on de-referencing)
            if curstate.board.side == root.board.side:
                curstate.prev.best_val = min(curstate.prev.best_val, est_heuristic) \
                    if curstate.prev.best_val else est_heuristic
                if curstate.prev.beta > est_heuristic:
                    curstate.prev.beta = est_heuristic
                    # found a better value, so reset patience
                    curstate.prev.patience = 3
                    curstate.prev.best_move = curstate.prev_move
                else:
                    # bad value, maybe future values are worse?
                    curstate.prev.patience -= 1
            else:
                curstate.prev.best_val = max(curstate.prev.best_val, -est_heuristic) \
                    if curstate.prev.best_val else -est_heuristic
                # negative since HEURISTICS are INVERTED for opponent, convert once to standardize for whole tree
                if curstate.prev.alpha < -est_heuristic:
                    curstate.prev.alpha = -est_heuristic
                    # found a better value, so reset patience
                    curstate.prev.patience = 3
                    curstate.prev.best_move = curstate.prev_move
                else:
                    # bad value, maybe future values are worse?
                    curstate.prev.patience -= 1
            # return to parent
            curnode = (None, curstate.prev)
        # no moves left to assess or ran out of patience or player cannot get better moves (if opponent plays optimally)
        elif (not curstate.next and curstate.best_val) or not curstate.patience or curstate.alpha >= curstate.beta:
            if curstate.prev:
                if curstate.board.side == root.board.side:
                    curstate.prev.best_val = min(curstate.prev.best_val,
                                                 curstate.best_val) if curstate.prev.best_val else curstate.best_val
                    if curstate.prev.beta > curstate.best_val:
                        curstate.prev.beta = curstate.best_val
                        # found a better value, so reset patience
                        curstate.prev.patience = 3
                        curstate.prev.best_move = curstate.prev_move
                    else:
                        # bad value, maybe future values are worse?
                        curstate.prev.patience -= 1
                else:
                    curstate.prev.best_val = max(curstate.prev.best_val,
                                                 curstate.best_val) if curstate.prev.best_val else curstate.best_val
                    if curstate.prev.alpha < curstate.best_val:
                        curstate.prev.alpha = curstate.best_val
                        # found a better value, so reset patience
                        curstate.prev.patience = 3
                        curstate.prev.best_move = curstate.prev_move
                    else:
                        # bad value, maybe future values are worse?
                        curstate.prev.patience -= 1
            curnode = (None, curstate.prev)
        else:
            # fresh node, not leaf and has depth remaining, expand and traverse to next node
            if not curstate.next:
                curstate.generate_ply()
            curnode = curstate.get_next()
            expanded += 1
    return root.best_move


def to_string(side, board):
    string = side
    for row in board:
        string += "".join(row)
    return string


def main():
    # book = populate_opening_book()
    file = open("input.txt", "r")
    # X or O
    player = file.readline().rstrip()
    time = float(file.readline().split()[0])
    prompt = []
    # 12x12 board layout
    for _ in range(12):
        prompt.append([*file.readline().rstrip()])
    file.close()
    board = Board(player, prompt)
    if board.pcount + board.ocount < 36:
        opening_book = {'O..........................XO..........OX'
                        '................................................................XO..........OX'
                        '..........................': [[22, 48, (7, 8)], [169, 408, (1, 2)], [75, 120, (9, 10)]],
                        'O..........................XXX.........OX'
                        '....................................................O...........OO..........OX'
                        '..........................': [[2, 8, (1, 4)], [5, 8, (3, 4)]],
                        'O................O.........XOX........XXX'
                        '....................................................O...........OO..........OX'
                        '..........................': [[0, 4, (4, 3)]],
                        'O.....X..........X.........XXX........XXO...........O'
                        '........................................O...........OO..........OX'
                        '..........................': [[0, 3, (2, 1)]],
                        'O.....X..........X.......XXXXX........XOO...........O'
                        '........................................O...........OO..........OX'
                        '..........................': [[0, 3, (1, 2)]],
                        'O...X.X........X.X.......XXOXX........XOO...........O'
                        '........................................O...........OO..........OX'
                        '..........................': [[0, 3, (0, 2)]],
                        'O.XXX.X........X.X.......XXOXX........XOO...........O'
                        '........................................O...........OO..........OX'
                        '..........................': [[0, 3, (1, 3)]],
                        'O.XXXXX........XXX.......XXXOX........XOO...........O'
                        '........................................O...........OO..........OX'
                        '..........................': [[0, 2, (1, 1)]],
                        'O.XXXXX.......OXXX.......XXXOX........XXX..........XO'
                        '........................................O...........OO..........OX'
                        '..........................': [[0, 2, (1, 5)]],
                        'OXXXXXX.......XOOOO......XXXOX........XXX..........XO'
                        '........................................O...........OO..........OX'
                        '..........................': [[0, 2, (9, 10)]],
                        'OXXXXXXX......XOOOX......XXXOX........XXX..........XO'
                        '........................................O...........OO..........OOO'
                        '.........................': [[0, 2, (3, 4)]],
                        'OXXXXXXX......XOXOX......XXXOX........XXXXX........XO'
                        '........................................O...........OO..........OOO'
                        '.........................': [[0, 2, (4, 4)]],
                        'OXXXXXXX......XOXXX......XXXXXX.......XXXOX........XOO'
                        '.......................................O...........OO..........OOO'
                        '.........................': [[0, 2, (3, 0)]],
                        'OXXXXXXX......XOXXX......XXXXXX......OXXOOX.......XXOO'
                        '.......................................O...........OO..........OOO'
                        '.........................': [[0, 2, (1, 6)]],
                        'X..........................XO..........OX'
                        '....................................................O...........OO..........OX'
                        '..........................': [[9, 16, (2, 4)], [16, 26, (1, 3)], [1, 6, (7, 7)]],
                        'X................O.........XOX.........OX'
                        '....................................................O...........OO..........OX'
                        '..........................': [[4, 4, (3, 1)], [2, 4, (1, 3)]],
                        'X................O.........XOX........XXO...........O'
                        '........................................O...........OO..........OX'
                        '..........................': [[3, 3, (0, 5)], [1, 1, (4, 4)]],
                        'X.....X..........X........OXXX........XOO...........O'
                        '........................................O...........OO..........OX'
                        '..........................': [[3, 3, (2, 0)]],
                        'X.....X........O.X.......XXOXX........XOO...........O'
                        '........................................O...........OO..........OX'
                        '..........................': [[3, 3, (0, 3)]],
                        'X..OX.X........O.X.......XXOXX........XOO...........O'
                        '........................................O...........OO..........OX'
                        '..........................': [[3, 3, (0, 1)]],
                        'X.XXX.X........XOX.......XXOOX........XOO...........O'
                        '........................................O...........OO..........OX'
                        '..........................': [[2, 2, (0, 4)], [1, 1, (4, 1)]],
                        'X.XXXXX.......OXXX.......XXOOX........XOO...........O'
                        '........................................O...........OO..........OX'
                        '..........................': [[2, 2, (4, 2)]],
                        'X.XXXXX.......OOOOO......XXXOX........XXX..........XO'
                        '........................................O...........OO..........OX'
                        '..........................': [[2, 2, (0, 0)]],
                        'XXXXXXX.......XOOOO......XXXOX........XXX..........XO'
                        '........................................O...........OO..........OOO'
                        '.........................': [[2, 2, (0, 6)]],
                        'XXXXXXXX......XOOOX......XXXOO........XXXO.........XO'
                        '........................................O...........OO..........OOO'
                        '.........................': [[2, 2, (3, 5)]],
                        'XXXXXXXX......XOXOX......XXXOO........XXXOX........XOO'
                        '.......................................O...........OO..........OOO'
                        '.........................': [[2, 2, (2, 5)]],
                        'XXXXXXXX......XOXXX......XOXXXX......OOOOOX........XOO'
                        '.......................................O...........OO..........OOO'
                        '.........................': [[2, 2, (4, 1)]],
                        'XXXXXXXX......XOOOOO.....XXXXXO......OXXOOX.......XXOO'
                        '.......................................O...........OO..........OOO'
                        '.........................': [[2, 2, (1, 7)]],
                        'O...............X..........XX..........OX'
                        '....................................................O...........OO..........OX'
                        '..........................': [[10, 26, (1, 2)]],
                        'O..............OX.........XXX..........OX'
                        '....................................................O...........OO..........OX'
                        '..........................': [[1, 7, (3, 0)], [1, 7, (1, 0)]],
                        'O..............OX........XXXX........O.OX'
                        '....................................................O...........OO..........OX'
                        '..........................': [[1, 4, (1, 0)]],
                        'O............O.OX........OOXX........O.OX'
                        '....................................................O...........OO.........XXX'
                        '..........................': [[1, 2, (2, 4)]],
                        'O............OXXX........OOXOO.......O.OX'
                        '....................................................O...........OO.........XXX'
                        '..........................': [[1, 2, (10, 6)]],
                        'O............OXXX........OOXXO.......O.OXX'
                        '...................................................O...........OO.........OXX........O'
                        '.................': [[0, 1, (9, 10)]],
                        'O............OXXX........OOXXXX......O.OXX'
                        '...................................................O...........OO.........OOOO.......O'
                        '.................': [[0, 1, (3, 5)]],
                        'O............OXXX........OOXXXX......O.OXXO.........X'
                        '........................................O...........OO.........OOOO.......O'
                        '.................': [[0, 1, (2, 6)]],
                        'O............OXXX........OXXOOOO.....OXXXXO.........X'
                        '........................................O...........OO.........OOOO.......O'
                        '.................': [[0, 1, (4, 2)]],
                        'O............OXXX........OXXOOOO.....OOXXXO........OXX'
                        '.......................................O...........OO.........OOOO.......O'
                        '.................': [[0, 1, (5, 3)]],
                        'O............OXXXX.......OXXXXOO.....OOXOXO........OOO..........O'
                        '............................O...........OO.........OOOO.......O.................': [[0, 1,
                                                                                                              (0,
                                                                                                               0)]],
                        'OOX..........OXXXX.......OXOXXOO.....OOXOXO........OOO..........O'
                        '............................O...........OO.........OOOO.......O.................': [[0, 1,
                                                                                                              (0,
                                                                                                               2)]],
                        'OOOOX........OOXXX.......OXOXOOO.....OOXOXO........OOO..........O'
                        '............................O...........OO.........OOOO.......O.................': [[0, 1,
                                                                                                              (1,
                                                                                                               5)]],
                        'X..............OX..........OX..........OX'
                        '....................................................O...........OO..........OX'
                        '..........................': [[12, 14, (2, 1)], [3, 6, (4, 1)], [1, 6, (1, 1)]],
                        'X..............OX.........OXX........O.OX'
                        '....................................................O...........OO..........OX'
                        '..........................': [[3, 4, (2, 0)], [1, 1, (4, 1)], [1, 1, (0, 1)], [1, 1, (3,
                                                                                                               1)]],
                        'X............O.OX........OOXX........O.OX'
                        '....................................................O...........OO..........OX'
                        '..........................': [[1, 2, (9, 7)], [1, 1, (0, 2)], [1, 2, (4, 1)]],
                        'X............O.OX........OOOOO.......O.OX'
                        '....................................................O...........OO.........XXX'
                        '..........................': [[1, 2, (1, 1)]],
                        'X............OXXX........OOXOO.......O.OX'
                        '....................................................O...........OO.........OXX........O'
                        '.................': [[1, 1, (3, 4)], [0, 1, (7, 10)]],
                        'X............OXXX........OOXXO.......O.OXX'
                        '...................................................O...........OO.........OOOO.......O'
                        '.................': [[1, 1, (2, 5)]],
                        'X............OXXX........OOXXXX......O.OOOO'
                        '..................................................O...........OO.........OOOO.......O'
                        '.................': [[1, 1, (4, 3)]],
                        'X............OXXX........OOOOOOO.....O.OXXO.........X'
                        '........................................O...........OO.........OOOO.......O'
                        '.................': [[1, 1, (3, 1)]],
                        'X............OXXX........OXXOOOO.....OOXOXO........OX'
                        '........................................O...........OO.........OOOO.......O'
                        '.................': [[1, 1, (4, 4)]],
                        'X............OXXX........OXXOOOO.....OOXOXO........OOO..........O'
                        '............................O...........OO.........OOOO.......O.................': [[1, 1,
                                                                                                              (1,
                                                                                                               4)]],
                        'XO...........OOXXX.......OXOXXOO.....OOXOXO........OOO..........O'
                        '............................O...........OO.........OOOO.......O.................': [[1, 1,
                                                                                                              (0,
                                                                                                               1)]],
                        'XOOO.........OOOOX.......OXOXOOO.....OOXOXO........OOO..........O'
                        '............................O...........OO.........OOOO.......O.................': [[1, 1,
                                                                                                              (0,
                                                                                                               3)]],
                        'XOOOX........OOOOOO......OXOXOOO.....OOXOXO........OOO..........O'
                        '............................O...........OO.........OOOO.......O.................': [[1, 1,
                                                                                                              (0,
                                                                                                               4)]],
                        'O...............XO.........XXX.........OX'
                        '....................................................O...........OO..........OX'
                        '..........................': [[2, 4, (3, 4)]],
                        'O.....X.........XX.........XXO.........OOO'
                        '...................................................O...........OO..........OX'
                        '..........................': [[0, 1, (0, 3)]],
                        'O...O.X........XXX.........XOO.........OOO'
                        '...................................................O...........OO..........OX'
                        '..........................': [[0, 1, (9, 10)]],
                        'O...O.X........XXX.........XXO.........OXO..........X'
                        '........................................O...........OO..........OOO'
                        '.........................': [[0, 1, (0, 2)]],
                        'O..OO.X........OOXX........OXX.........OXO..........X'
                        '........................................O...........OO..........OOO'
                        '.........................': [[0, 1, (2, 5)]],
                        'O..OO.X........OOOX........OOOO.......XXXO..........X'
                        '........................................O...........OO..........OOO'
                        '.........................': [[0, 1, (4, 1)]],
                        'O..OO.X........OOXX........OXOO.......XXXO........X.X........X'
                        '...............................O...........OO..........OOO.........................': [[0,
                                                                                                                 1,
                                                                                                                 (0,
        str_board = to_string(board.side, board.state)
        potential = []
        bad_moves = []
        # could go with highest win-rate move but chose to make bot non-deterministic instead for ZANE factor
        if str_board in opening_book:
            for wins, total, move in opening_book[str_board]:
                # add positive win-rate moves only, otherwise too much zane
                if wins / total > 0.5:
                    potential.append(move)
                else:
                    bad_moves.append(move)
        if potential:
            res = potential[random.randrange(len(potential))]
            outfile = open("output.txt", "w")
            # convert array notation into human-readable format
            outfile.write(f'{chr(97 + res[1])}{res[0] + 1}')
            outfile.close()
            return
        # inefficient, could improve
        for bm in bad_moves:
            for i in range(len(board.pmoves)):
                if bm == board.pmoves[i][0]:
                    board.pmoves.pop(i)
                    break
    # establishes computing power
    # calibrate.py runs before this
    cali = open("calibrate.txt", "r")
    # how much time to expand 1 node
    time_elapsed, node_count = cali.readline().rstrip().split()
    time_per_node = float(time_elapsed) / int(node_count)
    cali.close()
    depth = 0
    # 2 second flexibility made for mid-game boards, where a deeper search is important (unless no time)
    mid_game_extra_time = 2 if 36 < board.pcount + board.ocount < 108 else 0
    # static plus 2 since early and late game moves don't take much time
    time_per_move = time * 2 / (144 - board.pcount - board.ocount) + mid_game_extra_time + 2
    est_nodes = 1
    # can maybe support 6 depth on a more powerful pc
    for i in range(1, 7):
        # each depth increases amount of nodes expanded by 7x on worst case (so far)
        est_nodes *= 7
        if time_per_move < est_nodes * time_per_node:
            depth = i - 1
            break
    print(depth)
    res = alpha_beta_minimax(board, depth, time_per_move / time_per_node)
    outfile = open("output.txt", "w")
    # convert array notation into human-readable format
    outfile.write(f'{chr(97 + res[1])}{res[0] + 1}')
    outfile.close()


if __name__ == '__main__':
    main()