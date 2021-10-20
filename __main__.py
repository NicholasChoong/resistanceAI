import random
import numpy as np
from rich.console import Console
from rich.traceback import install

from s21980614.random_agent import RandomAgent
from s21980614.br_agent import BRAgent
from s21980614.game import Game

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
        # RejectAgent(name="r1"),
        # RejectAgent(name="r2"),
        # RejectAgent(name="r3"),
        # RejectAgent(name="r4"),
        # RejectAgent(name="r5"),
        # RejectAgent(name="r6"),
        # RejectAgent(name="r7"),
        # RandomAgent(name="r1"),
        # RandomAgent(name="r2"),
        # RandomAgent(name="r3"),
        # RandomAgent(name="r4"),
        # RandomAgent(name="r5"),
        # RandomAgent(name="r6"),
        # RandomAgent(name="r7"),
        BRAgent(name="1"),
        BRAgent(name="2"),
        BRAgent(name="3"),
        BRAgent(name="4"),
        BRAgent(name="5"),
        # BRAgent(name="6"),
        # BRAgent(name="7"),
        # BRAgent(name="8"),
        # BRAgent(name="9"),
        # BRAgent(name="10"),
    ]

    total_wins = 0
    number_of_games = 1000
    for _ in range(number_of_games):
        seed = 0
        if SEED:
            random.seed(SEED)
            np.random.seed(SEED)
        else:
            seed = random.randrange(0, 2 ** 32 - 1)
            random.seed(seed)
            np.random.seed(seed)
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

# Seed:  2521288640
# Seed:  1539842963
# Seed:  1051247700
# Seed:  4220499009
# Seed:  772275764
# Seed:  1048521470
# Seed:  921622142
# Seed:  645094810
# Seed:  1852503608
