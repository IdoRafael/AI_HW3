import csv
import os
import time
from run_game import *
import sys

T = (2, 10, 50)
Game_List = []
playerDict = {1: 'simple_player', 2: 'AI3_300816634_029993060.better_h_player',
              3: 'AI3_300816634_029993060.improved_player', 4: 'AI3_300816634_029993060.improved_better_h_player'}
winneresList = []
startingTime = time.ctime()
exprimentFilePath= "./experiment.csv"

def writeOutput(filename, gameList):
    with open(filename, "a") as ofile:
        for item in gameList:
            itemAsString = str(item)
            ofile.write(itemAsString)
            ofile.write(",")
        ofile.write("\n")

    print("finished writing to", filename, flush=True)


def returnRBscores(winner):
    if (winner == TIE):
        redScore = 0.5
        blackScore = 0.5
    elif (winner[0]=='red'):
        redScore = 1
        blackScore = 0
    elif (winner[0] == 'black'):
        redScore = 0
        blackScore = 1
    else:
        sys.exit("Total Failure when returning winner: ",winner,". at:", time.ctime())
    return redScore, blackScore

def runGame(i,j,t):
    winner = GameRunner( 2, t, 5, 'n', playerDict[i], playerDict[j]).run()
    print("winner is:", winner,  "finished at:", time.ctime(), flush=True)
    winneresList.append(winner)
    redScore, blackScore = returnRBscores(winner)
    single_game_list = [playerDict[i], playerDict[j], t, redScore, blackScore]
    writeOutput(exprimentFilePath, single_game_list)

############MAIN STARTS HERE####################################
if __name__ == '__main__':
    for t in T:
        print("section t=", t,"started at:",time.ctime(), flush=True)
        for i in range (1,4):
            for j in range (i+1, 5):
                print( playerDict[i],"vs.", playerDict[j], "started at:", time.ctime(), flush=True)
                runGame(i,j,t)
                print( playerDict[j],"vs.", playerDict[i], "started at:", time.ctime(), flush=True)
                runGame(j,i,t)
        print("section t=", t,"finished at:",time.ctime(), flush=True)
