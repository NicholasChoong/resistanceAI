from random_agent import RandomAgent
from game import Game
from agent import my_agent

agents = [RandomAgent(name='r1'), 
        RandomAgent(name='r2'),  
        RandomAgent(name='r3'),  
        RandomAgent(name='r4'),  
        RandomAgent(name='r5'),  
        RandomAgent(name='r6'),  
        RandomAgent(name='r7'),
        my_agent(name='r8'),
        #my_agent(name='r9'),
        #my_agent(name='r10')
        ]

total_wins = 0
number_of_games = 1

for i in range(number_of_games):
        game = Game(agents)
        game.play()
        if game.missions_lost < 3:
                total_wins += 1
# print(game)
print("Total wins for resistance: " + str(total_wins)+"/"+str(number_of_games))
print("Total wins for spies: " + str(number_of_games-total_wins)+"/"+str(number_of_games))


