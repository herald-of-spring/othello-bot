# import heapq
#
#
# class FutureState:
#     def __init__(self, n, b, d, p, pm, alpha, beta):
#         self.board = b
#         self.depth = d
#         self.prev = p
#         # what move brought us here
#         self.prev_move = pm
#         self.next = []
#         heapq.heapify(self.next)
#         self.alpha = alpha
#         self.beta = beta
#         # carry best value heuristic after search back to root
#         self.best_val = None
#         # remembers best move to save future computation time (only for depth >= 6)
#         self.best_move = None
#         # number of consecutive prunes before the rest of the nodes are abandoned entirely
#         # i.e. assumes the rest of the moves are bad, since original list of moves are ordered
#         self.patience = 3
#         self.name = n
#
#     def get_next(self):
#         updated = heapq.heappop(self.next)
#         updated[1].alpha, updated[1].beta = self.alpha, self.beta
#         return updated
#
#
# def alpha_beta_minimax(state):
#     # may save future computation time
#     # remember = None
#     # very low time, cannot think, or if only 1 move
#     # if not ply_depth or len(state.pmoves) == 1:
#     #     return state.pmoves[0][0]  # , remember
#     # alpha = -100000 | beta = 100000
#     root = state
#     curnode = (0, root)
#     # recursion ineffective, (modified) dfs instead
#     while curnode[1]:
#         est_heuristic, curstate = curnode
#         print(est_heuristic, curstate.board, curstate.depth, curstate.best_val, curstate.name)
#         # check suitable depth reached or end game state
#         if not curstate.depth:
#             # current node is player side -> parent node is opponent side (saves time on de-referencing)
#             if curstate.board == root.board:
#                 curstate.prev.best_val = min(curstate.prev.best_val, est_heuristic) \
#                     if curstate.prev.best_val else est_heuristic
#                 if curstate.prev.beta > est_heuristic:
#                     curstate.prev.beta = est_heuristic
#                     # found a better value, so reset patience
#                     curstate.prev.patience = 3
#                     curstate.prev.best_move = curstate.prev_move
#                 else:
#                     # bad value, maybe future values are worse?
#                     curstate.prev.patience -= 1
#             else:
#                 curstate.prev.best_val = max(curstate.prev.best_val, -est_heuristic) \
#                     if curstate.prev.best_val else -est_heuristic
#                 # negative since HEURISTICS are INVERTED for opponent, convert once to standardize for whole tree
#                 if curstate.prev.alpha < -est_heuristic:
#                     curstate.prev.alpha = -est_heuristic
#                     # found a better value, so reset patience
#                     curstate.prev.patience = 3
#                     curstate.prev.best_move = curstate.prev_move
#                 else:
#                     # bad value, maybe future values are worse?
#                     curstate.prev.patience -= 1
#             # return to parent
#             curnode = (None, curstate.prev)
#         # no moves left to assess or ran out of patience or player cannot get better moves (if opponent plays optimally)
#         elif (not curstate.next and curstate.best_val) or not curstate.patience or curstate.alpha >= curstate.beta:
#             if curstate.prev:
#                 if curstate.board == root.board:
#                     curstate.prev.best_val = min(curstate.prev.best_val,
#                                                  curstate.best_val) if curstate.prev.best_val else curstate.best_val
#                     if curstate.prev.beta > curstate.best_val:
#                         curstate.prev.beta = curstate.best_val
#                         # found a better value, so reset patience
#                         curstate.prev.patience = 3
#                         curstate.prev.best_move = curstate.prev_move
#                     else:
#                         # bad value, maybe future values are worse?
#                         curstate.prev.patience -= 1
#                 else:
#                     curstate.prev.best_val = max(curstate.prev.best_val,
#                                                  curstate.best_val) if curstate.prev.best_val else curstate.best_val
#                     if curstate.prev.alpha < curstate.best_val:
#                         curstate.prev.alpha = curstate.best_val
#                         # found a better value, so reset patience
#                         curstate.prev.patience = 3
#                         curstate.prev.best_move = curstate.prev_move
#                     else:
#                         # bad value, maybe future values are worse?
#                         curstate.prev.patience -= 1
#             curnode = (None, curstate.prev)
#         else:
#             curnode = curstate.get_next()
#     return root.best_move
import random


def to_string(side, board):
    string = side
    for row in board:
        string += "".join(row)
    return string

if __name__ == '__main__':
    player = "X"
    prompt = [list("............"),
              list(".O.X........"),
              list("XXXX........"),
              list("..OX........"),
              list(".OOO........"),
              list("...OO......."),
              list("....OO......"),
              list(".....O..O..."),
              list(".......XOXX."),
              list("........OXX."),
              list("........OXX."),
              list("............")]
    openings = {"X.............O.X........XXXX..........OX.........OOO...........OO...........OO...........O..O"
                "..........XOXX.........OXX.........OXX.............": [[3, 4, (0, 0)], [2, 3, (5, 5)]]}
    str_board = to_string(player, prompt)
    potential = []
    # could go with highest win-rate move but chose to make bot non-deterministic instead for ZANE factor
    if str_board in openings:
        for wins, total, move in openings[str_board]:
            # add positive win-rate moves only, otherwise too much zane
            if wins / total > 0.5:
                potential.append(move)
    if potential:
        print(potential[random.randrange(len(potential))])
    # a = FutureState('a', 1, 3, None, None, -100000, 100000)
    # b = FutureState('b', 0, 2, a, 'b', -100000, 100000)
    # c = FutureState('c', 0, 2, a, 'c', -100000, 100000)
    # heapq.heappush(a.next, (-7, b))
    # heapq.heappush(a.next, (0, c))
    # d = FutureState('d', 1, 1, b, 'd', -100000, 100000)
    # e = FutureState('e', 0, 1, b, 'e', -100000, 100000)
    # heapq.heappush(b.next, (4, d))
    # heapq.heappush(b.next, (-6, e))
    # f = FutureState('f', 1, 1, c, 'f', -100000, 100000)
    # g = FutureState('g', 1, 1, c, 'g', -100000, 100000)
    # heapq.heappush(c.next, (1, f))
    # heapq.heappush(c.next, (0, g))
    # h = FutureState('h', 0, 0, d, 'h', -100000, 100000)
    # i = FutureState('i', 0, 0, d, 'i', -100000, 100000)
    # p = FutureState('p', 0, 0, d, 'p', -100000, 100000)
    # q = FutureState('q', 0, 0, d, 'q', -100000, 100000)
    # r = FutureState('r', 0, 0, d, 'r', -100000, 100000)
    # heapq.heappush(d.next, (-3, h))
    # heapq.heappush(d.next, (-5, i))
    # heapq.heappush(d.next, (-2, p))
    # heapq.heappush(d.next, (-1, q))
    # heapq.heappush(d.next, (0, r))
    # j = FutureState('j', 1, 0, e, 'j', -100000, 100000)
    # k = FutureState('k', 1, 0, e, 'k', -100000, 100000)
    # heapq.heappush(e.next, (6, j))
    # heapq.heappush(e.next, (9, k))
    # l = FutureState('l', 0, 0, f, 'l', -100000, 100000)
    # m = FutureState('m', 0, 0, f, 'm', -100000, 100000)
    # heapq.heappush(f.next, (-1, l))
    # heapq.heappush(f.next, (-2, m))
    # n = FutureState('n', 0, 0, g, 'n', -100000, 100000)
    # o = FutureState('o', 0, 0, g, 'o', -100000, 100000)
    # heapq.heappush(g.next, (0, n))
    # heapq.heappush(g.next, (1, o))
    # print(alpha_beta_minimax(a))
    # print(a.best_val, a.best_move, a.alpha, a.beta)
    # print(b.best_val, b.best_move, b.alpha, b.beta)
    # print(c.best_val, c.best_move, c.alpha, c.beta)
    # print(d.best_val, d.best_move, d.alpha, d.beta)
    # print(e.best_val, e.best_move, e.alpha, e.beta)
    # print(f.best_val, f.best_move, f.alpha, f.beta)
    # print(g.best_val, g.best_move, g.alpha, g.beta)
    # print(h.best_val, h.best_move, h.alpha, h.beta)
    # print(i.best_val, i.best_move, i.alpha, i.beta)
    # print(j.best_val, j.best_move, j.alpha, j.beta)
    # print(k.best_val, k.best_move, k.alpha, k.beta)
    # print(l.best_val, l.best_move, l.alpha, l.beta)
    # print(m.best_val, m.best_move, m.alpha, m.beta)
    # print(n.best_val, n.best_move, n.alpha, n.beta)
    # print(o.best_val, o.best_move, o.alpha, o.beta)
    # print(p.best_val, p.best_move, p.alpha, p.beta)
    # print(q.best_val, q.best_move, q.alpha, q.beta)
    # print(r.best_val, r.best_move, r.alpha, r.beta)
