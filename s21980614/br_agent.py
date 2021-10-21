from rich.console import Console
from rich.traceback import install
from .agent import Agent
from typing import Tuple
import numpy as np
from itertools import combinations, islice
import random

console = Console()
install(show_locals=True)
DEBUG = False
PLAYER_NUMBER = 0


class BRAgent(Agent):
    """
    new_game and *_outcome methods simply inform agents of events that have occured,
    while propose_mission, vote, and betray require the agent to commit some action.
    """

    # voting_blunder = 0.2

    def __init__(self, name: str = "21980614") -> None:
        """
        Initialises the agent, and gives it a name.
        You can add configuration parameters etc here,
        but the default code will always assume a 1-parameter
        constructor, which is the agent's name.
        The agent will persist between games to allow for long-term learning etc.

        Args:
            name (str, optional):
                The student number.
                Defaults to "21980614".
        """
        self.name: str = name

    def new_game(
        self, number_of_players: int, player_number: int, spy_list: list[int]
    ) -> None:
        """
        Initialises a new game.
        The agent should drop their current gameState and reinitialise
        all their game variables.

        Args:
            number_of_players (int):
                The number of players in the game.
            player_number (int):
                An id number for this agent in the game.
            spy_list (list[int]):
                A list of agent indexes, which is the set of spies if this agent is
                a spy, or an empty list if this agent is not a spy.
        """
        self.player_number: int = player_number
        self.number_of_players: int = number_of_players
        self.players_list: list[int] = list(range(number_of_players))

        self.number_of_spies: int = self.spy_count[number_of_players]
        self.spy: bool = bool(spy_list)
        self.spy_list: list[int] = spy_list
        self.resistance_list: list[int] = list(set(self.players_list) - set(spy_list))
        self.players_list: list[int] = list(range(number_of_players))
        self.sus_table: dict[int, float] = {}

        self.leader: int = -1
        self.mission_team: list[int] = []
        self.sitting_out_team: list[int] = []
        self.yep_votes: list[int] = []
        self.nop_votes: list[int] = []
        self.number_of_rounds_on_mission: int = 0
        self.number_of_betrayers: int = 0

        self.successful_missions: int = 0
        self.failed_missions: int = 0
        self.total_mission: int = 0

        self.init_sus_table(number_of_players, player_number, self.number_of_spies)

    def is_spy(self):
        """
        returns True iff the agent is a spy
        """
        return self.player_number in self.spy_list

    def propose_mission(self, team_size: int, betrayals_required: int = 1) -> list[int]:
        """
        This method is called when the agent is required to lead (propose) a mission.

        Args:
            team_size (int):
                The number of agents to go on the mission.
            betrayals_required (int, optional):
                The number of betrayals required for the mission to fail.
                Defaults to 1.

        Returns:
            list[int]:
                A team_size list of distinct agents with id between 0 and number_of_players.
        """
        team_mission = []
        if self.spy:
            # Choose the members of the resistance first
            team_mission = list(
                np.random.choice(
                    self.resistance_list, team_size - betrayals_required, False
                )
            )
            # Choose itself as it is the leader
            team_mission.append(self.player_number)
            filtered_spy_list = self.spy_list[:]
            filtered_spy_list.remove(self.player_number)
            # Choose more spies to sabotage mission
            if betrayals_required > 1:
                more_spies = list(
                    np.random.choice(filtered_spy_list, betrayals_required - 1, False)
                )
                team_mission += more_spies
        elif self.total_mission == 0:
            # First round, randomly choose players and then itself
            filtered_players_list = self.players_list[:]
            filtered_players_list.remove(self.player_number)
            team_mission = list(
                np.random.choice(filtered_players_list, team_size - 1, False)
            )
            team_mission.append(self.player_number)
        else:
            # Choose players from sus table
            sorted_sus_table = {
                k: v
                for k, v in sorted(self.sus_table.items(), key=lambda item: item[1])
            }
            # Group the players by their sus points
            grouped_by_values = {}
            for key, value in sorted_sus_table.items():
                grouped_by_values.setdefault(value, []).append(key)
            for _, player_group in grouped_by_values.items():
                if len(team_mission) == team_size:
                    break
                vacancies = team_size - len(team_mission)
                if len(player_group) <= team_size and len(player_group) <= vacancies:
                    for player in player_group:
                        team_mission.append(player)
                elif len(player_group) <= team_size:
                    selected_players = list(
                        np.random.choice(player_group, vacancies, False)
                    )
                    team_mission += selected_players
                else:
                    team_mission = list(
                        np.random.choice(player_group, team_size, False)
                    )
            if self.player_number not in team_mission:
                random_index = random.randint(0, team_size - 1)
                team_mission[random_index] = self.player_number
        return team_mission

    def vote(self, mission: list[int], leader: int) -> bool:
        """
        This method is called when an agent is required to vote on
        whether a mission should proceed.

        Args:
            mission (list[int]):
                A list of unique agents to be sent on a mission.
            leader (int):
                The index of the player who proposed the mission
                between 0 and number_of_players.

        Returns:
            bool:
                True if the vote is for the mission, and
                False if the vote is against the mission.
        """
        self.leader = leader
        self.mission_team = mission
        self.sitting_out_team = list(set(self.players_list) - set(mission))

        if self.number_of_rounds_on_mission == 4:
            return True
        if self.total_mission == 0:
            return True
        if leader == self.player_number:
            return True

        if self.spy:
            spies_on_mission = self.get_spies_on_mission()
            if self.failed_missions == 2 or spies_on_mission:
                return True
            if spies_on_mission == len(mission):
                return False
        elif self.player_number not in mission:
            return False
        else:
            sorted_sus_table = {
                k: v
                for k, v in sorted(self.sus_table.items(), key=lambda item: item[1])
            }
            minimum_probability = 0.0
            mission_probability = 0.0
            sliced_sorted_sus_table = dict(
                islice(sorted_sus_table.items(), len(mission))
            )
            minimum_probability = sum(sliced_sorted_sus_table.values())
            for player in mission:
                mission_probability += self.sus_table[player]
            if mission_probability > minimum_probability + (minimum_probability / 10):
                return False
        return True

    def betray(self, mission: list[int], leader: int) -> bool:
        """
        This method is called on an agent who has a choiceto betray (fail)
        the mission.
        Only spies are permitted to betray the mission.

        Args:
            mission (list[int]):
                A list of unique agents to be sent on a mission.
            leader (int):
                The index of the player who proposed the mission
                between 0 and number_of_players.

        Returns:
            bool:
                True if this agent chooses to betray the mission, False otherwise.
        """
        if not self.spy:
            return False

        if len(mission) == 2:
            return False
        if self.failed_missions == 2:
            return True
        if self.failed_missions == 1 and self.total_mission == 4:
            return True
        betrayals_required = self.fails_required[self.number_of_players][
            self.total_mission
        ]
        spies_on_mission = self.get_spies_on_mission()
        if spies_on_mission <= betrayals_required:
            return True
        else:
            return random.random() < 0.7

    def vote_outcome(self, mission: list[int], leader: int, votes: list[int]) -> None:
        """
        The method is called on an agent to inform them of the outcome of a vote,
        and which agent voted for or against the mission.

        Args:
            mission (list[int]):
                A list of unique agents to be sent on a mission.
            leader (int):
                The index of the player who proposed the mission
                between 0 and number_of_players.
            votes (list[int]):
                A dictionary mapping player indexes to Booleans.
                True if they voted for the mission, False otherwise.
        """
        self.number_of_rounds_on_mission += 1
        self.yep_votes = votes
        self.nop_votes = list(set(self.players_list) - set(votes))
        if self.number_of_rounds_on_mission == 5:
            for players in self.nop_votes:
                pass

    def mission_outcome(
        self, mission: list[int], leader: int, betrayals: int, mission_success: bool
    ) -> None:
        """
        Informs all agents of the outcome of the mission, including
        the number of agents who failed the mission.

        Args:
            mission (list[int]):
                A list of unique agents to be sent on a mission.
            leader (int):
                The index of the player who proposed the mission
                between 0 and number_of_players.
            betrayals (int):
                The number of people on the mission who betrayed the mission.
            mission_success (bool):
                True if there were not enough betrayals to cause the mission
                to fail, False otherwise.
        """
        if mission_success:
            self.successful_missions += 1

    def round_outcome(self, rounds_complete: int, missions_failed: int) -> None:
        """
        Informs all agents of the game state at the end of the round.

        Args:
            rounds_complete (int):
                The number of rounds (0-5) that have been completed.
            missions_failed (int):
                The number of missions (0-3) that have failed.
        """
        self.number_of_rounds_on_mission = 0
        self.total_mission = rounds_complete
        self.failed_missions = missions_failed
        if DEBUG and not self.spy and self.player_number == PLAYER_NUMBER:
            console.log("round:", self.total_mission)
            console.log("player:", self.player_number)
            sorted_sus_table = {
                k: v
                for k, v in sorted(self.sus_table.items(), key=lambda item: item[1])
            }
            console.log(sorted_sus_table)
            console.log()
        self.update_sus_table()

    def game_outcome(self, spies_win: bool, spies: list[int]) -> None:
        """
        Informs all agents of the outcome of the game, including
        the identity of the spies.

        Args:
            spies_win (bool):
                True iff the spies caused 3+ missions to fail.
            spies (list[int]):
                A list of the player indexes for the spies.
        """
        if DEBUG and not self.spy:
            console.log("round:", self.total_mission)
            console.log("player:", self.player_number)
            sorted_sus_table = {
                k: v
                for k, v in sorted(self.sus_table.items(), key=lambda item: item[1])
            }
            console.log(sorted_sus_table)
            console.log("spies: ", sorted(spies))
            console.log()

    def get_spies_on_mission(self) -> int:
        """Gets the number of spies in the mission.

        Returns:
            int:
                The number of spies.
        """
        return len(set(self.spy_list).intersection(set(self.mission_team)))

    def init_sus_table(
        self, number_of_players: int, player_number: int, number_of_spies: int
    ) -> None:
        """
        Initialisse a dictionary with player index as the key and
        its suspicion point as the value.
        Divide the number of spies by the number of player minus this agent
        to get the suspicion point for the other players.

        Args:
            number_of_players (int):
                The number of players in the game.
            player_number (int):
                An id number for this agent in the game.
            number_of_spies (int):
                The number of spies in the game
        """
        sus_point = number_of_spies / (number_of_players - 1)
        self.sus_table = dict.fromkeys(self.players_list, sus_point)
        self.sus_table[player_number] = 0.0

    def bayes_rule(self, pA: float, pB: float, pBa: float) -> float:
        """
        Calculates probability based on Bayes' rule.
        Bayes' rule:
            P(A|B) = [P(B|A) * P(A)] / P(B)

        Args:
            pA (float):
                The probability A being a spy.
            pB (float):
                The probability B being a mission outcome.
            pBa (float):
                The probability Ba being the mission outcome given A is a spy.

        Returns:
            float:
                pAb The probability Ab being A is a spy given B is the mission outcome.
        """
        if not pB:
            return 0.0
        return (pBa * pA) / pB

    def get_probabilities(
        self, mission: list[int], combinations_list: list[Tuple[int, ...]]
    ) -> float:
        """Calculates pB and pBa.

        Args:
            mission (list[int]):
                A list of unique agents to be sent on a mission.
            combinations_list (list[Tuple[int, ...]]):
                A list of tuples of spies being on the mission.

        Returns:
            float:
                The probability of pB.
        """
        pB = 0.0
        for spies in combinations_list:
            pB = 0.0
            pBx = 1.0
            resistances = list(set(mission) - set(spies))
            for spy in spies:
                pBx *= self.sus_table[spy]
            for resistance in resistances:
                pBx *= 1 - self.sus_table[resistance]
            pB += pBx
        if not pB:
            return 1.0
        return pB

    def update_sus_table(self) -> None:
        """
        Updates the sus_table.
        """
        combinations_for_mission_team = list(
            combinations(self.mission_team, self.number_of_betrayers)
        )
        combinations_for_sitting_out_team = list(
            combinations(
                self.sitting_out_team, self.number_of_spies - self.number_of_betrayers
            )
        )
        for player in self.players_list:
            pA, pB, pAb, pBa = 0.0, 0.0, 0.0, 0.0
            pA = self.sus_table[player]
            if player in self.mission_team:
                combinations_list = self.mission_team[:]
                combinations_list.remove(player)
                combinations_list = [tuple(combinations_list)]
                pBa = self.get_probabilities(self.mission_team, combinations_list)
                pB = self.get_probabilities(
                    self.mission_team, combinations_for_mission_team
                )
            else:
                combinations_list = self.sitting_out_team[:]
                combinations_list.remove(player)
                combinations_list = [tuple(combinations_list)]
                pBa = self.get_probabilities(self.sitting_out_team, combinations_list)
                # pB = self.get_probabilities(
                #     self.sitting_out_team, combinations_for_sitting_out_team
                # )
                pB = self.get_probabilities(self.sitting_out_team, combinations_list)
            pAb = self.bayes_rule(pA, pB, pBa)
            if DEBUG and not self.spy and self.player_number == PLAYER_NUMBER:
                console.log(
                    "Round:",
                    self.total_mission,
                    "Player:",
                    player,
                    "Mission:",
                    player in self.mission_team,
                    "pA:",
                    pA,
                    "pB:",
                    pB,
                    "pBa:",
                    pBa,
                    "pAb:",
                    pAb,
                    "\n",
                )
            if (
                DEBUG
                and not self.spy
                and self.player_number == PLAYER_NUMBER
                and player in [1, 2]
            ):
                console.log(f"Sus_point {player}:", pAb)
            self.sus_table[player] = pAb


if __name__ == "__main__":
    a = BRAgent("21980614")
    a.new_game(7, 2, [])
    a.players_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    a.mission_team = [0, 1, 2, 3]
    # a.init_sus_table(7, 2, 2)
    # console.log(a.sus_table)
    # a.spy_list = [1, 3, 5]
    # console.log(a.get_spies_on_mission())
    # console.log(list(np.random.choice(a.players_list, 5, False)))
    # a.players_list += [7, 8, 9]
    # console.log(a.players_list)
    # b: dict[int, float] = {0: 1.0, 1: 4.0, 2: 3.0, 3: 2.0, 4: 5.0}
    # c = {k: v for k, v in sorted(b.items(), key=lambda item: item[1])}
    # d = dict(islice(c.items(), 3))
    # console.log(b)
    # console.log(c)
    # console.log(list(d.keys()))
    # console.log(a.players_list)
    # console.log(a.propose_mission(2))
    # b = list(combinations(a.mission_team, 2)
    # )
    mission_team = [1, 2, 3, 4, 5, 5, 5, 2, 6]
    # spy_list = [1, 4, 6, 7]
    # console.log(list(set(spy_list).intersection(set(mission_team))))
    # console.log(list(set(spy_list) - set(mission_team)))
    # console.log(list(set(mission_team) - set((1, 2, 3))))

    # console.log(tuple(mission_team))
    # z: Tuple[int, ...] = tuple(mission_team)
    # console.log(z)
    # n = "asdad [blue]wadaw[/blue]:"
    # console.log(n)

    # random.seed(1)
    # np.random.seed(1)
    # console.log(list(combinations(mission_team, 2)))
    # console.log(np.random.choice(mission_team, 3, False))
    g = {
        1: 123,
        2: 123,
        3: 1233423234234234234234,
        4: 12234243,
        5: 123,
        6: 122343,
        7: 123,
    }
    res = {}
    for key, value in sorted(g.items()):
        res.setdefault(value, []).append(key)
    # console.log(res.items())
    console.log(random.randint(0, 1))

    # asdf = [0.4, 0.5, 0.6, 0.7, 0.8]
    # product = 1.0
    # for number in asdf:
    #     product *= 1 - number
    # console.log(product)
    asd = list(np.random.choice(a.players_list, 5, False))
    console.log(asd)
    console.log([1, 2] + [2, 3])
