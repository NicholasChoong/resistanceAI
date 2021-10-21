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

SEED = 1
LOG = False

if __name__ == "__main__":
    if SEED:
        random.seed(SEED)
    seed = 0
    seeds = []
    agents = [
        BayeBehaviourAgent(name="BayeBehaviourAgent"),
        # BRAgent(name="BRAgent1"),
        # BRAgent(name="BRAgent2"),
        # BRAgent(name="BRAgent3"),
        # BRAgent(name="BRAgent4"),
        # BRAgent(name="BRAgent5"),
        # BRAgent(name="BRAgent6"),
        # BRAgent(name="BRAgent7"),
        # BRAgent(name="BRAgent8"),
        # BRAgent(name="BRAgent9"),
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
        # BayeBehaviourAgent(name="BayeBehaviourAgent5"),
        # BayeBehaviourAgent(name="BayeBehaviourAgent6"),
        # BayeBehaviourAgent(name="BayeBehaviourAgent7"),
        # BayeBehaviourAgent(name="BayeBehaviourAgent8"),
        # BayeBehaviourAgent(name="BayeBehaviourAgent9"),
    ]

    roles_assigned = False
    total_wins = 0
    number_of_games = 10
    for _ in track(range(number_of_games), description="Playing..."):
        seed = random.randrange(0, 2 ** 32 - 1)
        seeds.append(seed)
        # console.log(seed)
        random.seed(seed)
        np.random.seed(seed)
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
    console.log(
        f"Seeds Test: {len(set(seeds) & set([577090037,2364836463,1991203165,3271461370,3457313376,521895542,2909462035,3441764289,3451104866,1337851119,]))== len(seeds)}"
    )
    console.log(f"Seed: {seed}")
    console.log(f"Assigned roles: {roles_assigned}")
    console.log(f"Number of players: {len(agents)}")
    console.log(f"Resistance win rate: {(total_wins/number_of_games)*100:.2f}%")
    console.log(
        f"Spy win rate: {((number_of_games - total_wins)/number_of_games)*100:.2f}%"
    )
    console.log(f"Total wins: {total_wins} / {number_of_games}")
    console.log("######################################")
    console.log(log_locals=True)
