# creates tournaments of bots to train and try to achieve better heuristic values
# initially planned 12 matches to confidently determine which bot was better but since bots
# are deterministic (no randomness) there is no need
# can also build opening books from a set of heuristics in history.txt
# CPU intensive program! TRAIN AT YOUR OWN RISK!

import multiprocessing
import random
import bot
import datetime


# returns the bot that won; if tied, the one that won 'harder' (more disc difference)
def match(bot1, bot2, visuals):
    one_side = startmatch(bot1, bot2, visuals, False)
    other_side = startmatch(bot2, bot1, visuals, False)
    if one_side > 0 > other_side:
        w = bot1
    elif one_side < 0 < other_side:
        w = bot2
    else:
        w = bot1 if one_side - other_side > 0 else bot2
    return w


# plays a match between 2 bots, with bot1 going first, returns positive value if bot1 wins, negative if bot2 wins
# played on static depth of 4 moves
def startmatch(bot1, bot2, visuals, logging):
    player1 = "O"
    player2 = "X"
    state = [list("............"),
             list("............"),
             list("..XO........"),
             list("..OX........"),
             list("............"),
             list("............"),
             list("............"),
             list("............"),
             list("........XO.."),
             list("........OX.."),
             list("............"),
             list("............")]
    # if both flags false, game ends
    flag1 = True
    flag2 = True
    # additionally prints board if visuals or record move made if logging
    move1 = []
    move2 = []
    # board representation in flattened string, if logging
    str_board = 0
    # only logging until 35 pieces on board - end of early game
    pieces = 8
    while flag1 or flag2:
        if logging and pieces < 36:
            str_board = to_string('O', state)
        state, coord, flag1 = bot.main(bot1, player1, state)
        if visuals and flag1:
            print("O plays ---------------")
            for row in state:
                print(row)
        if logging and pieces < 36:
            # bot1 made a move, record it
            if flag1:
                move1.append((str_board, coord))
                pieces += 1
            str_board = to_string('X', state)
        state, coord, flag2 = bot.main(bot2, player2, state)
        if visuals and flag2:
            print("X plays ---------------")
            for row in state:
                print(row)
        if logging and flag2 and pieces < 36:
            move2.append((str_board, coord))
            pieces += 1
    if visuals:
        print("End state ---------------")
        for row in state:
            print(row)
    total1 = 0
    total2 = 1
    for row in state:
        for tile in row:
            if tile == 'O':
                total1 += 1
            elif tile == 'X':
                total2 += 1
    if visuals:
        print(bot1 if total1 - total2 > 0 else bot2)
    # additionally return various move success rate statistics in logging mode
    return (total1 - total2) if not logging else (bot1, total1, move1, bot2, total2, move2)


# converts board information into 145 char string - 1st char denotes next to move
def to_string(side, board):
    string = side
    for row in board:
        string += "".join(row)
    return string


def callback(c):
    winners.append(c)


def robin_callback(c):
    robin1, t1, move1, robin2, t2, move2 = c
    if tuple(robin1) not in records:
        # wins as (O, X)
        records[tuple(robin1)] = [0, 0]
    if tuple(robin2) not in records:
        # wins as (O, X)
        records[tuple(robin2)] = [0, 0]
    # updates winner records
    records[tuple(robin1)][0] += 1 if t1 > t2 else 0
    records[tuple(robin2)][1] += 1 if t1 < t2 else 0
    # adds move to opening book if it does not yet exist, or modifies it
    for str_board, m in move1:
        if str_board not in openings:
            openings[str_board] = [[1 if t1 > t2 else 0, 1, m]]
        else:
            flag = False
            for move_stats in openings[str_board]:
                if m == move_stats[2]:
                    move_stats[0] += 1 if t1 > t2 else 0
                    move_stats[1] += 1
                    flag = True
                    break
            if not flag:
                openings[str_board].append([1 if t1 > t2 else 0, 1, m])
    for str_board, m in move2:
        if str_board not in openings:
            openings[str_board] = [[1 if t1 < t2 else 0, 1, m]]
        else:
            flag = False
            for move_stats in openings[str_board]:
                if m == move_stats[2]:
                    move_stats[0] += 1 if t1 < t2 else 0
                    move_stats[1] += 1
                    flag = True
                    break
            if not flag:
                openings[str_board].append([1 if t1 < t2 else 0, 1, m])


if __name__ == '__main__':
    # set to True for match to display on command line, 1 match only
    sampleMatch = False
    # set to True to log opening moves (< 36 discs on board) and write to openings.txt
    learning = False
    if sampleMatch:
        match([-0.4, 90, -0.1, 70, 0.7, -35, 0.2, 25, 0.6, -85],
              [-1.0, 60, -0.25, 85, 0.75, -90, 1.0, 100, -0.95, -50], True)
    elif learning:
        # round-robin tournament on 'refined' bots in history.txt
        robin = [[-0.4, 90, -0.1, 70, 0.7, -35, 0.2, 25, 0.6, -85],
                 [-0.1, 70, -0.3, 80, 0.55, -40, -0.1, 30, 0.3, -45]]
        with open("history.txt", "r") as file:
            for line in file:
                if line[0] == '[':
                    robin.append(eval(line.rstrip()))
        records = {}
        openings = {}
        for bot in robin:
            pool = multiprocessing.Pool(processes=len(robin))
            for i in range(len(robin)):
                pool.apply_async(startmatch, args=(bot, robin[i], False, True), callback=robin_callback)
            pool.close()
            pool.join()
        print("Final Scoring:")
        for bot, wins in records.items():
            print(wins[0], wins[1], bot)
        # writes to file a flattened board as string and associated statistics
        # format: {XXOX.XOX.......O.XOO....OXOO.XO...: [[wins, total, move], [wins, total, move]...], ...}
        file = open("openings.txt", "w")
        file.write(str(openings))
        file.close()
    else:
        try:
            file = open("genetic_data.txt", "r+")
            # format [[a1, a2, b1, b2, c1, c2, d1, d2, e1, e2], ...]
            # 10 values of heuristics
            # 16 heuristics: 2 from top 2 in previous generation, 8 from genetic, 4 from hill-climbing, 2 new random
            gen_data = eval(file.readline().rstrip())
            # train for 10 generations
            it = 10
            gen = 4
            # getting 11 iterations for now, took 2 days at 4 hours each
            while it < 12:
                while len(gen_data) > 2:
                    # Top 16 -> top 8 -> top 4 -> top 2 -> save
                    pool = multiprocessing.Pool(processes=len(gen_data) // 2)
                    winners = []
                    for i in range(1, len(gen_data), 2):
                        pool.apply_async(match, args=(gen_data[i - 1], gen_data[i], False), callback=callback)
                    pool.close()
                    pool.join()
                    gen_data = winners
                gen += 1
                print(it, gen, gen_data)
                if gen == 10:
                    print(datetime.datetime.now().time())
                    # saves winning iterations in history.txt
                    save = open("history.txt", "a")
                    save.write("__________________Iteration " + str(it) + "____________________\n")
                    save.write(str(gen_data[0]) + "\n")
                    save.write(str(gen_data[1]) + "\n")
                    save.close()
                    gen = 0
                    it += 1
                    # seeds new population
                    next_gen = []
                    for _ in range(16):
                        temp = []
                        for _ in range(5):
                            normalize = 0.05
                            for _ in range(2):
                                temp.append(round(random.randint(-20, 20) * normalize, 3))
                                normalize *= 100
                        next_gen.append(temp)
                else:
                    # top 2
                    next_gen = [gen_data[0], gen_data[1]]
                    repeats = set()
                    # 8 genetic children
                    for _ in range(4):
                        a, b = random.sample([0, 1, 2, 3, 4], 2)
                        # new unique sample
                        while (a, b) in repeats:
                            a, b = random.sample([0, 1, 2, 3, 4], 2)
                        repeats.add((a, b))
                        temp1 = []
                        temp2 = []
                        for i in range(5):
                            # crossing over by ratio, not value (only value if ratio is div by 0)
                            if i == b:
                                across1 = gen_data[1][b * 2] / gen_data[1][a * 2] * gen_data[0][a * 2] \
                                    if gen_data[1][a * 2] else gen_data[1][b * 2]
                                bcross1 = gen_data[1][b * 2 + 1] / gen_data[1][a * 2 + 1] * gen_data[0][a * 2 + 1] \
                                    if gen_data[1][a * 2 + 1] else gen_data[1][b * 2 + 1]
                                across2 = gen_data[0][b * 2] / gen_data[0][a * 2] * gen_data[1][a * 2] \
                                    if gen_data[0][a * 2] else gen_data[0][b * 2]
                                bcross2 = gen_data[0][b * 2 + 1] / gen_data[0][a * 2 + 1] * gen_data[1][a * 2 + 1] \
                                    if gen_data[0][a * 2 + 1] else gen_data[0][b * 2 + 1]
                                temp1.append(round(across1, 3))
                                temp1.append(round(bcross1, 1))
                                temp2.append(round(across2, 3))
                                temp2.append(round(bcross2, 1))
                            else:
                                temp1.append(gen_data[0][i * 2])
                                temp1.append(gen_data[0][i * 2 + 1])
                                temp2.append(gen_data[1][i * 2])
                                temp2.append(gen_data[1][i * 2 + 1])
                        next_gen.append(temp1)
                        next_gen.append(temp2)
                    # 4 hill-climb children
                    for i in range(2):
                        repeats = set()
                        for _ in range(2):
                            a, b = random.choices([0, 1, 2, 3, 4], k=2)
                            while (a, b) in repeats:
                                a, b = random.choices([0, 1, 2, 3, 4], k=2)
                            repeats.add((a, b))
                            temp = []
                            for j in range(5):
                                # slight in/decrement
                                temp.append(round(gen_data[i][j * 2] +
                                                  (random.choice([-0.05, 0.05]) if j == a else 0), 3))
                                temp.append(round(gen_data[i][j * 2 + 1] +
                                                  (random.choice([-5, 5]) if j == b else 0), 1))
                            next_gen.append(temp)
                    # 2 completely random children
                    for _ in range(2):
                        temp = []
                        for _ in range(5):
                            normalize = 0.05
                            for _ in range(2):
                                temp.append(round(random.randint(-20, 20) * normalize, 3))
                                normalize *= 100
                        next_gen.append(temp)
                    random.shuffle(next_gen)
                file.seek(0)
                file.write(str(next_gen))
                file.truncate()
                gen_data = next_gen
            file.close()
        except FileNotFoundError:
            # seeding file with 16 random heuristic values
            file = open("genetic_data.txt", "w")
            gen_data = []
            for _ in range(16):
                temp = []
                for _ in range(5):
                    normalize = 0.05
                    for _ in range(2):
                        temp.append(round(random.randint(-20, 20) * normalize, 3))
                        normalize *= 100
                gen_data.append(temp)
            file.write(str(gen_data))
            file.close()
            print("Seeding complete, run program again to train")
