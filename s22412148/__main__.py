from random_agent import RandomAgent
from custom_agent import BayeBehaviourAgent
from game import Game

agents = [BayeBehaviourAgent(name='r1'), 
        BayeBehaviourAgent(name='r2'),  
        BayeBehaviourAgent(name='r3'),  
        BayeBehaviourAgent(name='r4'),  
        BayeBehaviourAgent(name='r5'),  
        BayeBehaviourAgent(name='r6'),  
        BayeBehaviourAgent(name='r7'),
        BayeBehaviourAgent(name='r8'),
        BayeBehaviourAgent(name='r9'),
        BayeBehaviourAgent(name='r10')
        ]

total_wins = 0
number_of_games = 10000

for i in range(number_of_games):
        game = Game(agents)
        game.play()
        if game.missions_lost < 3:
                total_wins += 1
# print(game)
print("Total wins for resistance: " + str(total_wins)+"/"+str(number_of_games))
print("Total wins for spies: " + str(number_of_games-total_wins)+"/"+str(number_of_games))


