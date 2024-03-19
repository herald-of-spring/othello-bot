# calibrate benchmarks computing power to aid the main bot in deciding how deep it needs to search

import copy
import heapq
from collections import deque
import time


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

    # player's stable discs - opponent stable discs
    # def stability_heuristic(self):
    #     return 0

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
        # metric to measure early/mid/late game by how many discs on the board, as a cubic function
        tcount = self.pcount + self.ocount
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
            obj = FutureState(Board(switch_sides, copy.deepcopy(self.board.state)),
                              self.depth, self, None, self.alpha, self.beta)
            self.next = [(obj.board.heuristic, None, obj)]
        else:
            # generate board if move was played
            for moveset in self.board.pmoves:
                move = moveset[0]
                changes = moveset[1]
                new_board = copy.deepcopy(self.board.state)
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
def alpha_beta_minimax(state, ply_depth):
    # may save future computation time
    # remember = None
    # very low time, cannot think, or if only 1 move
    if not ply_depth or len(state.pmoves) == 1:
        return state.pmoves[0][0]  # , remember
    # alpha = -100000000 | beta = 100000000
    root = FutureState(state, ply_depth * 2, None, None, -1e9, 1e9)
    curnode = (state.heuristic, root)
    expanded = 0
    # recursion ineffective, (modified) dfs instead
    while curnode[1]:
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
    return root.best_move, expanded


def main():
    player = "O"
    prompt = [list("............"),
              list("....O......."),
              list("..XOX......."),
              list(".XXX........"),
              list("............"),
              list("............"),
              list("............"),
              list("........O..."),
              list("........OO.."),
              list("........OX.."),
              list("............"),
              list("............")]
    board = Board(player, prompt)
    # times how long and how many nodes expanded each depth search takes
    start = time.time()
    # calculate time per node
    move, expanded = alpha_beta_minimax(board, 3)
    print(move)
    time_per_node = time.time() - start
    outfile = open("calibrate.txt", "w")
    outfile.write(str(time_per_node) + " " + str(expanded))
    outfile.close()


if __name__ == '__main__':
    main()
