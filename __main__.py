import random
import numpy as np
from rich.console import Console
from rich.traceback import install
from rich.progress import track
import csv

from s21980614.game import Game
from s21980614.random_agent import RandomAgent
from s21980614.br_agent import BRAgent
from s21980614.agent import Agent
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
    agents = [
        # BayeBehaviourAgent(name="BayeBehaviourAgent Res 1"),
        # BRAgent(name="BRAgent Spy 1"),
        # BRAgent(name="BRAgent Spy 2"),
        # BRAgent(name="BRAgent Spy 3"),
        # BRAgent(name="BRAgent Spy 4"),
        # BayeBehaviourAgent(name="BayeBehaviourAgent Res 2"),
        # BayeBehaviourAgent(name="BayeBehaviourAgent Res 3"),
        # # BayeBehaviourAgent(name="BayeBehaviourAgent Res 4"),
        # # BayeBehaviourAgent(name="BayeBehaviourAgent Res 5"),
        # BayeBehaviourAgent(name="BayeBehaviourAgent Res 6"),
        # BRAgent(name="BRAgent"),
        BRAgent(name="BRAgent Res 1"),
        BayeBehaviourAgent(name="BayeBehaviourAgent Spy 1"),
        BayeBehaviourAgent(name="BayeBehaviourAgent Spy 2"),
        # BayeBehaviourAgent(name="BayeBehaviourAgent Spy 3"),
        # BayeBehaviourAgent(name="BayeBehaviourAgent Spy 4"),
        BRAgent(name="BRAgent Res 2"),
        BRAgent(name="BRAgent Res 3"),
        # BRAgent(name="BRAgent Res 4"),
        # BRAgent(name="BRAgent Res 5"),
        # BRAgent(name="BRAgent Res 6"),
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
        # StatAgent(name="StatAgent5"),
        # StatAgent(name="StatAgent6"),
        # StatAgent(name="StatAgent7"),
        # StatAgent(name="StatAgent8"),
        # StatAgent(name="StatAgent9")
        # ExpertAgent(name="ExpertAgent Spy"),
        # BayeBehaviourAgent(name="BayeBehaviourAgent"),
        # BayeBehaviourAgent(name="BayeBehaviourAgent"),
        # BayeBehaviourAgent(name="BayeBehaviourAgent1"),
        # BayeBehaviourAgent(name="BayeBehaviourAgent2"),
        # BayeBehaviourAgent(name="BayeBehaviourAgent3"),
        # BayeBehaviourAgent(name="BayeBehaviourAgent4"),
        # BayeBehaviourAgent(name="BayeBehaviourAgent5"),
        # BayeBehaviourAgent(name="BayeBehaviourAgent6"),
        # BayeBehaviourAgent(name="BayeBehaviourAgent7"),
        # BayeBehaviourAgent(name="BayeBehaviourAgent8"),
        # BayeBehaviourAgent(name="BayeBehaviourAgent9"),
    ]

    roles_assigned = True
    total_wins = 0
    number_of_games = 10000
    a = Agent(name="Testing")
    for number_of_players in range(len(agents), len(agents) + 1):
        suspected_spies_list: list[list[int]] = []
        for _ in track(range(number_of_games), description="Playing..."):
            seed = random.randrange(0, 2 ** 32 - 1)
            random.seed(seed)
            np.random.seed(seed)
            game = Game(agents[0:number_of_players], roles_assigned)
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
            sorted_sus_table = {
                k: v
                for k, v in sorted(
                    agents[0].get_sus_table().items(), key=lambda item: item[1]
                )
            }
            suspected_spies_list.append(
                list(sorted_sus_table.keys())[
                    number_of_players
                    - a.spy_count[number_of_players] : number_of_players
                ]
            )
            if game.missions_lost < 3:
                total_wins += 1
        console.log("######################################")
        results: list[str] = []
        for suspected_spies in suspected_spies_list:
            if 1 in suspected_spies or 2 in suspected_spies:
                results.append("1")
            else:
                results.append("0")
        console.log(f"Successful Accusation: {results.count('1')} / {number_of_games}")
        with open(
            f"BRAgent_res_vs_BBAgent_spy_{number_of_players}P.csv", "w", newline=""
        ) as file:
            write = csv.writer(file)
            write.writerows(results)
        console.log(f"Seed: {seed if not SEED else SEED}")
        console.log(f"Assigned roles: {roles_assigned}")
        console.log(f"Number of players: {len(agents[0:number_of_players])}")
        console.log(f"Resistance win rate: {(total_wins/number_of_games)*100:.2f}%")
        console.log(
            f"Spy win rate: {((number_of_games - total_wins)/number_of_games)*100:.2f}%"
        )
        console.log(f"Total wins: {total_wins} / {number_of_games}")
        console.log("######################################")
        console.log()
    # console.log(log_locals=True)
