import random
import numpy as np
from rich.console import Console
from rich.traceback import install
from rich.progress import track

from s21980614.game import Game
from s21980614.random_agent import RandomAgent
from s21980614.br_agent import BRAgent
from s21980614.learners import StatAgent
from s21980614.experts import ExpertAgent
from s22412148.baye_behaviour_agent import BayeBehaviourAgent

install(show_locals=True)

console = Console()

SEED = 0
DEBUG = False

if __name__ == "__main__":
    seed = 0
    if SEED:
        random.seed(SEED)
        np.random.seed(SEED)
    else:
        seed = random.randrange(0, 2 ** 32 - 1)
        random.seed(seed)
        np.random.seed(seed)

    agents = [
        BRAgent(name="BRAgent"),
        BayeBehaviourAgent(name="BayeBehaviourAgent"),
        ExpertAgent(name="ExpertAgent 1"),
        ExpertAgent(name="ExpertAgent 2"),
        StatAgent(name="StatAgent"),
    ]

    total_wins = 0
    number_of_games = 10000
    for _ in track(range(number_of_games), description="Playing..."):
        game = Game(agents)
        game.play()
        if DEBUG:
            console.log("Seed: ", seed)
            # console.log(game)
            console.log(game.__str__())
            console.log("Game won: ", game.missions_lost < 3)
            # console.print(game.__str__())
        if game.missions_lost < 3:
            total_wins += 1
    console.log(f"Number of players: {len(agents)}")
    console.log(f"Win rate: {(total_wins/number_of_games)*100:.1f}%")
    console.log(f"Total wins: {total_wins} / {number_of_games}", log_locals=True)
