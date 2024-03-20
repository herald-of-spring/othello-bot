# Othello/Reversi Game Playing Agent
This month-long project aims to create an Othello bot using a modified alpha-beta pruning search method and improve performance by training heuristics. 

However, it plays a *modified* version of Othello - 12x12, 300 second limit for each player, [O] moves first, [X] gets 1 tiebreaker point, and starting configurations [O]: d3, c4, j9, i10 | [X]: c3, d4, i9, j10. As such, there has not been previous research for this particular version, which is the main challenge of the project.

Special thanks to Dr. Imre Leader for providing initial strategic insights for this modified Othello!

## General Usage
Run *calibrate.py* first, it generates file *calibrate.txt* which determines how powerful the CPU is and thus how far ahead the agent should look.

Then prepare *input.txt* with format as follows:  
Line 1: Next to move  
Line 2: Time left for player and (optionally) time left for opponent  
Lines 3-14: Board state with blank spaces as '.'  
A sample input file is given, which can be modified as necessary

Run *homework.py*, which reads *input.txt* and writes *output.txt* which is the move the agent has chosen.

## Training Usage
There are several modes within trainer.py - *sample match*, *learning*, and *training*. 

*Sample match*, when set to True (Line 147) will allow the manipulation of the 2x10 heuristics (more on this later) on Lines 151 and 152, which will face each other and with the visual aid of the board to see the status of the game.  

*Training* happens when **both** sample match and learning are False (default), which attempts to find good heuristics (more on how - *Part 3: Heuristic Training*) and logs them in *history.txt* (a sample is given - the result of 2 days of training). This is an **INTENSIVE PROCESS** that can take DAYS. Be warned!

*Learning*, when set to True (Line 149) will take the results of training and face them against each other in a round robin format and will output the tournament results in *round-robin-log.txt* (a sample is given - the tournament took 6 hours), each line indicates the wins playing as [O], wins as [X], and the heuristic values used.  
In addition, each move played in all the games of the tournament will be logged into an opening book, recording the success (wins, total) of each move, in *openings.txt* (provided, and is used in the current version of *homework.py*, more on opening books - *Part 4: Choosing the Correct Heuristic and Opening Books*). Again, this is an **INTENSIVE PROCESS**!

At a high level, running *trainer.py* calls *bot.py*, which is a near copy of *homework.py*, but returns different results (to aid with different output formats) and uses dynamic heuristics. When training or learning, it plays several matches at once, which requires high computing power.

## Part 1: Research and Game Rules
For someone who hasn't played Othello before, research on strategy is essential, and reading previous implementations of Othello agents even more so. The most helpful source for strategy is *Samsoft's Strategy Guide* - https://samsoft.org.uk/reversi/strategy.htm. It details several useful tactics to look out for, such as evaporation strategy, frontiers (and quiet moves), and introduces traps (although I am still unable to identify such scenarios).

An Othello game playing agent implementation by Vaishnavi Sannidhanam and Muthukaruppan Annamalai - https://courses.cs.washington.edu/courses/cse573/04au/Project/mini1/RUSSIA/Final_Paper.pdf - was immensely helpful in translating the strategy aforementioned into **heuristics**, which is, roughly put, **a measure of how good a board state is for a given side**.

## Part 2: Search Implementation - Alpha-beta Pruning
Minimax is an algorithm that picks the best next move by examining future board states to a certain depth and assumes that the opponent will also play their best move (i.e. no wishful thinking). **Alpha-beta pruning** is a variant of this, working faster by disregarding states that will never happen (if the opponent plays optimally, since if not, it would only be better for the player).

This agent uses this algorithm as the backbone for game playing, but modifies some aspects to attempt to optimize further. Before choosing which move to examine further, it sorts all possible moves in **descending heuristic values** (i.e. best moves first). The heuristics value is only a guess of how good a certain board is, but if it is a *good* guess, then odds are, it is a *good* move. This puts immense trust on the heuristic to be reliable as estimating a bad move as good will only waste search time.

The other modification is the **patience** value. By default set at 3, when examining a move that does not seem as good as one of the previous, **patience** wanes. And when no **patience** remains, the rest of the *unexamined moves* in the list are *abandoned entirely*. Since the list of moves is sorted, the agent assumes that all moves from here on are bad, and being impatient all but confirms it. However, this also means estimating a good move as bad will bury it deep in the move list, which may never get explored. As such, having a good heuristic is paramount and is the most important feature of the program.

## Part 3: Heuristic Training
But how does a heuristic know the best move? What makes a *good* move? For this agent, it measures several qualities of a board state - how many **corners** it controls compared to the opponent, how many more **moves** it has (relative to the opponent), how many more **discs** (and therefore points) it has, how many more discs it has in the **center** (defined as c3 to j10), and how many more **groups** (defined as clusters of pieces not joined vertically, horizontally, and diagonally) it has.

Each of these **5** qualities have **2** associated values (making **10** in total). It represents the linear formula *y = ax + b*, where *y* represents one of the 5 qualities, *a* and *b* its 2 values, and *x* the total amount of discs on the board. This creates a **dynamic heuristic** that is able to adapt according to the game state, since for example having fewer discs in the early game is generally favored but having more discs at the end is the objective of the game! 

All of these qualities are helpful in turning a dynamic game like Othello into a formula, which computers understand a bit (or several) better. Yet, not all qualities are made equal, and the challenge lies in striking the right balance of numbers to use in said formula.

From research and previous findings, corners seem to be most favored, then moves, and discs least of all. Central discs and groups are new custom qualities that had a novice Othello player's intuition to back it up. To adapt these heuristics into the dynamic linear formula format, the first (human) heuristic is generated:  
*Corners*: 8/10 early, 4/10 late  
*Mobility (moves)*: 9/10 early, 3/10 late  
*Disc count*: -3/10 (a detriment) early, 6/10 late  
*Center control*: 3/10 early, 0/10 late  
*Group count*: -4/10 (a detriment) early, 0/10 late  
Specifically, the numbers used are on Line 155 in *trainer.py* (Later, midway through training, another attempt is made and the second human heuristic is on Line 156)

But why think when you can automate? After all, computers may know something humans don't. Let's generate a bunch of random numbers, let the heuristics face each other, and repeat the process survivor-of-the-fittest style!  
The first generation consists of 16 randomly generated heuristics. They face off in a single elimination format and 2 survivors are saved to repopulate for the next generation.

**8** new heuristics are made by crossing the 2 survivors in a **genetic algorithm**. This aims to create children that (hopefully) carries the better parts of both parents to create an *even better* heuristic. In this instance, the ratio between 2 random qualities is chosen, the arithmetic details of which can be found at Lines 224 to 254 within *trainer.py*.  
**4** new heuristics are made by in/decrementing values, 2 from each survivor, which is similar to a **gradient descent algorithm**, except it is hard to determine whether such incremental change is good or bad. The details can be found at Lines 255 to 270.  
**2** old heuristics - the survivors.  
**2** new random heuristics to total **16** for the new generation, in case a better heuristic can suddenly be found once in a blue moon (*spoiler: the blue moon never happened during the 2 days of training*).

The single elimination tournaments happen for a total of **10 generations** (while training, the numbers seem to converge roughly 5-7 generations in) to return the final 2 survivors, which is considered 1 iteration (4-6 hours). **11 iterations** were performed over the course of 2 days.

## Part 4: Choosing the Correct Heuristic and Opening Books
Now armed with a wealth of heuristics, which one is the best? Are the computer-generated heuristics even as good as the human ones? The only way to find out is through a round-robin tournament between all **24** (22 generated, 2 human) heuristics. After 6 hours of intensive battle and computing, the results are in (*round-robin-log.txt*)! An initial glance pins *(1.4, -15.0, 0.85, 20.0, 0.1, 60.0, -0.4, -20.0, -0.3, -20.0)* as the winner with *20/24* wins as [O] and *22/24* as [X]. This heuristic follows such strategy:  
*Corners*: -1/10 early, 18/10 late  
*Mobility (moves)*: 2/10 early, 14/10 late  
*Disc count*: 6/10 early, 8/10 late  
*Center control*: -2/10 early, -8/10 late  
*Group count*: -2/10 early, -6/10 late  
Interesting strategy. For one, completely disregarding corners early on, known (at least amongst *humans*) as an indispensible asset in Othello.

Upon examining further, Iteration 11 (*history.txt*) has converged (so well?) to *2 copies* of one heuristic. This copy caused a slight disruption in statistics in that it actually had *10/24* as [O] and *11/24* as [X]. Even so, it is still better than the first human heuristic (painfully so). The actual best heuristic is then *(0.185, 55.6, 0.75, 25.0, 0.04, 9.1, -0.55, -15.0, 0.68, -13.6)* with *15/24* as [O] and *18/24* as [X]. Thus, the findings are:  
**Corners**: 6/10 early, 8/10 late  
**Mobility (moves)**: 3/10 early, 13/10 late  
**Disc count**: 1/10 early, 2/10 late  
**Center control**: -2/10 early, -8/10 late  
**Group count**: -1/10 early, 9/10 late  
In other words, corners are *always important*, mobility's *importance scales* with game state, disc count is (surprisingly) *unimportant*, central discs are *devastating*, and groups are *undesired* (late does not matter as much here as it becomes difficult to have many groups as the board fills up).

In addition, the next most valuable output from the round-robin tournament is game data to create an **opening book**. The concept of opening theory is that it allows the *bypassing* of thinking during the early game and delivering the agent into a smooth, *advantageous* mid game. As a result, the agent can readily capitalize whilst having more time on the clock. Opening books, however, require *extensive game databases*. They are usually curated from professional matches and catalogued according to *win-rate* and *play-rate*, which are in the *millions*.  

Because there are no established game databases to learn from (for *modified* Othello), the program has to make it itself, and not from professional level matches either. The largest moveset holds a *modest* 408 games, and that will have to do for now. The generated opening book can be found at *openings.txt*, which is then copied to *homework.py*.

## Part 5: Future Improvements
The **bottleneck** of the current algorithm lies in the fact that it still takes a long time to search, achieving a lookahead of **3-4 moves** on average. By comparison, a professional player can achieve a lookahead of 8 moves. To improve upon this search time, a *persistent text file* can be saved when the agent makes a move that results in the opponent skipping theirs. In the current version, the agent has to do the entire search again when it could have saved a sequence of moves since there is no interference from the opponent.

Another improvement, or rather *idea*, is to have a more detailed heuristic. Although undocumented, a *cubic implementation* (instead of linear as of the current version) is somewhat explored, but did not seem to garner effective results. Later, when transitioning to linear, a mistake in the code is found, but re-transitioning would sabotage the little training time that is left before project submission. Thus, cubic heuristic implementation deserves a revisit.

*I hope you have enjoyed reading my journey through game playing algorithms and findings. The project was most enjoyable as I code for many days and nurtured the various iterations to take seed. For any inquiries, further details, or if you simply want to show your improvements and ideas to this code (feel free to!), please email andy.ducanh@gmail.com*
