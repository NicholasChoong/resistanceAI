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
LOG = False

if __name__ == "__main__":
    seed = 0
    # seed = SEED or random.randrange(0, 2 ** 32 - 1)
    # random.seed(seed)
    # np.random.seed(seed)
    agents = [
        BayeBehaviourAgent(name="BayeBehaviourAgent"),
        # BRAgent(name="BRAgent1"),
        # BRAgent(name="BRAgent2"),
        # BRAgent(name="BRAgent3"),
        # BRAgent(name="BRAgent4"),
        # ExpertAgent(name="ExpertAgent Res"),
        # ExpertAgent(name="ExpertAgent Res1"),
        # ExpertAgent(name="ExpertAgent Res2"),
        # ExpertAgent(name="ExpertAgent Res3"),
        # ExpertAgent(name="ExpertAgent Res4"),
        # StatAgent(name="StatAgent"),
        # StatAgent(name="StatAgent1"),
        # StatAgent(name="StatAgent2"),
        # StatAgent(name="StatAgent3"),
        # StatAgent(name="StatAgent4"),
        # ExpertAgent(name="ExpertAgent Spy"),
        # BRAgent(name="BRAgent"),
        BayeBehaviourAgent(name="BayeBehaviourAgent1"),
        BayeBehaviourAgent(name="BayeBehaviourAgent2"),
        BayeBehaviourAgent(name="BayeBehaviourAgent3"),
        BayeBehaviourAgent(name="BayeBehaviourAgent4"),
    ]

    roles_assigned = False
    total_wins = 0
    number_of_games = 10
    for _ in track(range(number_of_games), description="Playing..."):
        game = Game(agents, roles_assigned)
        # game = Game(agents)
        game.play()
        if LOG:
            console.log()
            console.log("######################################")
            console.log("Seed: ", seed)
            # console.log(game)
            console.log(game.__str__())
            console.log("Game won: ", game.missions_lost < 3)
            # console.print(game.__str__())
            console.log("######################################")
            console.log()
        if game.missions_lost < 3:
            total_wins += 1
    console.log()
    console.log("######################################")
    console.log(f"Seed: {seed}")
    console.log(f"Number of players: {len(agents)}")
    console.log(f"Resistance win rate: {(total_wins/number_of_games)*100:.2f}%")
    console.log(
        f"Spy win rate: {((number_of_games - total_wins)/number_of_games)*100:.2f}%"
    )
    console.log(f"Total wins: {total_wins} / {number_of_games}", log_locals=True)
    console.log("######################################")
    console.log()
