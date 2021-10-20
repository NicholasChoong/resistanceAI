from random_agent import RandomAgent
from custom_agent import my_agent
from game import Game

agents = [my_agent(name='r1'), 
        my_agent(name='r2'),  
        my_agent(name='r3'),  
        my_agent(name='r4'),  
        my_agent(name='r5'),  
        my_agent(name='r6'),  
        my_agent(name='r7'),
        my_agent(name='r8'),
        #my_agent(name='r9'),
        #my_agent(name='r10')
        ]

total_wins = 0
number_of_games = 1000

for i in range(number_of_games):
        game = Game(agents)
        game.play()
        if game.missions_lost < 3:
                total_wins += 1
# print(game)
print("Total wins for resistance: " + str(total_wins)+"/"+str(number_of_games))
print("Total wins for spies: " + str(number_of_games-total_wins)+"/"+str(number_of_games))


