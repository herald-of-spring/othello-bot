# Othello/Reversi Game Playing Bot
This month-long project aims to create an Othello bot using a modified alpha-beta pruning search method and improve performance by training heuristics. 

However, it plays a modified version of Othello - 12x12, 300 second limit for each player, [O] moves first, [X] gets 1 tiebreaker point, and starting configurations [O]: d3, c4, j9, i10 | [X]: c3, d4, i9, j10. As such, there has not been previous research for this particular version, which is the main challenge of the project.

Special thanks to Dr. Imre Leader for providing initial strategic insights for this modified Othello!

## General Usage
Run calibrate.py first, it generates file calibrate.txt which determines how powerful the CPU is and thus how far ahead the bot should look.

Then prepare input.txt with format as follows:  
Line 1: Next to move  
Line 2: Time left for player and (optionally) time left for opponent
Lines 3-14: Board state with blank spaces as '.'  
A sample input file is given, which can be modified as necessary

Run homework.py, which reads input.txt and writes output.txt which is the move the bot has chosen.

## Training Usage
There are several modes within trainer.py - visual match, learning, and training. 

## Part 1: Research and Game Rules
For someone who hasn't played Othello before, research on strategy is essential, and reading previous implementations of Othello bots even more so. The most helpful source for strategy is Samsoft's Strategy Guide - https://samsoft.org.uk/reversi/strategy.htm. It details several useful tactics to look out for, such as evaporation strategy, frontiers (and quiet moves), and introduces traps (although I am still unable to identify such scenarios). An Othello bot implementation by Vaishnavi Sannidhanam and Muthukaruppan Annamalai -https://courses.cs.washington.edu/courses/cse573/04au/Project/mini1/RUSSIA/Final_Paper.pdf - was immensely helpful in 

## Part 2: Search Implementation - Alpha-beta Pruning
Minimax is an algorithm that picks the best move from

## Part 3: Heuristic Training
But how does one know the best move? What is a 'good' move?

## Part 4: Discussion and Future Improvements
