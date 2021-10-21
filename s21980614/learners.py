from rich.console import Console
from rich.traceback import install
import random
from collections import defaultdict
from .agent import Agent
from typing import Literal

console = Console()
install(show_locals=True)
DEBUG = False
LOG = False


class Variable(object):
    def __init__(self):
        self.total = 0
        self.samples = 0

    def sample(self, value):
        self.total += value
        self.samples += 1

    def estimate(self, number_of_players, number_of_spies):
        if self.samples > 0:
            return float(self.total) / float(self.samples)
        else:
            return number_of_spies / (number_of_players - 1)

    def __repr__(self):
        if self.samples:
            return "%0.2f%% (%i)" % (
                (100.0 * float(self.total) / float(self.samples)),
                self.samples,
            )
        else:
            return "UNKNOWN"


class GlobalStatistics(object):
    def __init__(self):
        self.spy_VotesForSpy = Variable()
        self.spy_VotesForRes = Variable()
        self.spy_PicksSpy = Variable()
        self.spy_PicksSelf = Variable()
        self.res_VotesForSpy = Variable()
        self.res_VotesForRes = Variable()
        self.res_PicksSpy = Variable()
        self.res_PicksSelf = Variable()
        self.spy_Sabotage = Variable()

    def __repr__(self):
        return """
As Spy, VOTES:  Spy %s  Res  %s
        PICKS:  Spy %s  Self %s
        SABOTAGE    %s
As Res, VOTES:  Spy %s  Res  %s
        PICKS:  Spy %s  Self %s
""" % (
            self.spy_VotesForSpy,
            self.spy_VotesForRes,
            self.spy_PicksSpy,
            self.spy_PicksSelf,
            self.spy_Sabotage,
            self.res_VotesForSpy,
            self.res_VotesForRes,
            self.res_PicksSpy,
            self.res_PicksSelf,
        )


class LocalStatistics(object):
    def __init__(self):
        self.probability = Variable()
        # Chances of being one of the two spies out of the other four are 50%.
        # self.probability.sample(number_of_spies / (number_of_players - 1))

    def update(self, probability):
        self.probability.sample(probability)


class StatAgent(Agent):
    """
    new_game and *_outcome methods simply inform agents of events that have occured,
    while propose_mission, vote, and betray require the agent to commit some action.
    """

    global_statistics = defaultdict(GlobalStatistics)

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
                An id number for the agent in the game
            spy_list (list[int]):
                A list of agent indexes, which is the set of spies if this agent is
                a spy, or an empty list if this agent is not a spy.
        """
        self.number_of_players: int = number_of_players
        self.player_number: int = player_number
        self.players: list[int] = list(range(number_of_players))
        self.spies: list[int] = spy_list
        self.spy: bool = bool(spy_list)
        self.spies_num: int = self.spy_count[number_of_players]
        self.total_mission: int = 0
        self.failed_missions: int = 0
        # self.successful_missions: int = 0
        self.local_statistics = defaultdict(LocalStatistics)
        for player in self.players:
            self.local_statistics[player].update(
                self.spies_num / (number_of_players - 1)
            )

        # self.leader: int = -1
        # self.team: list[int] = []
        self.missions: list[tuple[list[int], Literal[0, 1]]] = []
        self.selections: list[tuple[int, list[int]]] = []
        self.votes: list[tuple[list[int], list[int]]] = []

    def propose_mission(self, team_size: int, fails_required: int = 1) -> list[int]:
        """
        This method is called when the agent is required to lead (propose) a mission.

        Args:
            team_size (int):
                The number of agents to go on the mission
            fails_required (int, optional):
                The number of fails required for the mission to fail.
                Defaults to 1.

        Returns:
            list[int]:
                A team_size list of distinct agents with id between 0 and number_of_players.
        """
        # NOTE: The probability of each player depends on the team chosen.
        # As you pick players assuming they are not spies, the probabilities
        # should be updated here.
        team = [p for p in self.players if p == self.player_number]
        while len(team) < team_size:
            candidates = [p for p in self.players if p not in team]
            estimates = [1.0 - self._estimate(p) for p in candidates]
            self.candidates_table = list(zip(candidates, estimates))
            # console.log(list(self.candidates_table))
            # console.log(list(zip(candidates, estimates)))
            # console.log(list(self.candidates_table))
            team.append(self._roulette(self.candidates_table))
            # console.log("Team:", team)
        return team

    def vote(self, mission: list[int], leader: int) -> bool:
        """
        The method is called on an agent to inform them of the outcome
        of a vote, and which agent voted for or against the mission.

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
        # Store this for later once we know the spies.
        self.selections.append((leader, mission))

        # Hard coded if spy, could use statistics to check what to do best!
        if self.spy:
            return len([p for p in mission if p in self.spies]) > 0

        total = sum(self._estimate(p) for p in mission if p != self)
        alternate = sum(
            self._estimate(p) for p in self.players if p != self and p not in mission
        )
        return bool(total <= alternate)

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
        votese = []
        for player in self.players:
            if player in votes:
                votese.append(True)
            else:
                votese.append(False)
        # Step 2) Store.
        self.votes.append((votes, mission[:]))

        # Based on the voting, we can do many things:
        #   - Infer the probability of spies being on the team.
        #   - Infer the probability of spies being the voters.

        # Step 1) As resistance, run a bunch of predictions.
        # According to Bayes' Theorem:
        #   P(A|B) = P(B|A)  * P(A) / P(B)
        spied = bool(len([p for p in mission if p in self.spies]) > 0)
        # or self._discard(team)
        if spied:
            for player, vote in zip(self.players, votese):
                p = self.local_statistics[player].probability.estimate(
                    self.number_of_players, self.spies_num
                )

                # In this case with:
                #   - A is the probability of 'player' being a spy.
                #   - B is the probability of 'player' voting for suspects.
                if vote:
                    spy_Vote = self.fetch(player, ["spy_VotesForSpy"])
                    probability = spy_Vote * p  # / 1.0
                else:
                    res_Vote = self.fetch(player, ["res_VotesForSpy"])
                    probability = 1.0 - res_Vote * p  # / 1.0

                self.local_statistics[player].update(probability)
        elif False:
            # NOTE: If we had more information we could determine if a team excluded spies
            # for sure!  In this case, we could run more accurate predictions...
            for player, vote in zip(self.players, votese):
                spy_Vote = self.fetch(player, ["spy_VotesForSpy", "spy_VotesForRes"])
                res_Vote = self.fetch(player, ["res_VotesForSpy", "res_VotesForRes"])
                p = self.local_statistics[player].probability.estimate()

                # In this case with:
                #   - A is the probability of 'player' being a spy.
                #   - B is the probability of 'player' voting true.
                if vote:
                    probability = spy_Vote * p  # / 1.0
                else:
                    probability = 1.0 - res_Vote * p  # / 1.0

                self.local_statistics[player].update(probability)

        for player, vote in zip(self.players, votese):
            p = self.local_statistics[player].probability.estimate(
                self.number_of_players, self.spies_num
            )
            spy_Vote = self.fetch(player, ["spy_VotesForSpy"]) * (0.0 + p) + self.fetch(
                player, ["res_VotesForSpy"]
            ) * (1.0 - p)
            res_Vote = self.fetch(player, ["spy_VotesForRes"]) * (0.0 + p) + self.fetch(
                player, ["res_VotesForRes"]
            ) * (1.0 - p)

            for member in mission:
                # In this case, Bayes' Theorem with:
                #   - A is the probability of team 'member' being a spy.
                #   - B is the probability of 'player' voting true.
                t = self.local_statistics[member].probability.estimate(
                    self.number_of_players, self.spies_num
                )

                if vote:
                    probability = spy_Vote * t  # / 1.0
                else:
                    probability = 1.0 - res_Vote * t  # / 1.0

                # NOTE: This reduces overall estimate quality...
                # self.local_statistics[member.name].update(probability)

    def betray(self, mission: list[int], leader: int) -> bool:
        """
        This method is called on an agent who has a choice to betray (fail) the mission.
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
        return self.spy
        # if not self.spy:
        #     return False

        # if len(mission) == 2:
        #     return False
        # if self.failed_missions == 2:
        #     return True
        # if self.failed_missions == 1 and self.total_mission == 4:
        #     return True
        # betrayals_required = self.fails_required[self.number_of_players][
        #     self.total_mission
        # ]
        # spies_on_mission = len(set(self.spies).intersection(set(mission)))
        # if spies_on_mission <= betrayals_required:
        #     return True
        # else:
        #     return random.random() < 0.7

    def mission_outcome(
        self, mission: list[int], leader: int, num_fails: int, mission_success: bool
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
            num_fails (int):
                The number of people on the mission who betrayed the mission.
            mission_success (bool):
                True if there were not enough betrayals to cause the mission
                to fail, False otherwise.
        """
        sabotaged = 0 if mission_success else 1

        # Store this information for later once we know the spies.
        self.missions.append((mission[:], sabotaged))
        if self.spy:
            return

        # Update probabilities for this current game...
        others = [p for p in mission if p != self.player_number]
        probability = float(sabotaged) / float(len(others))
        for p in others:
            self.local_statistics[p].update(probability)

        probability = 1.0 - float(sabotaged) / float(
            self.number_of_players - len(others)
        )
        for p in [p for p in self.players if p not in mission]:
            self.local_statistics[p].update(probability)

    def round_outcome(self, rounds_complete: int, missions_failed: int) -> None:
        """
        Informs all agents of the game state at the end of the round.

        Args:
            rounds_complete (int):
                The number of rounds (0-5) that have been completed.
            missions_failed (int):
                The number of missions (0-3) that have failed.
        """
        self.total_mission = rounds_complete
        self.failed_missions = missions_failed

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
        for team, sabotaged in self.missions:
            suspects = [p for p in team if p in spies]
            # No spies on this mission to update statistics.
            if len(suspects) == 0:
                continue

            # This mission passed despite spies, very suspicious...
            for p in suspects:
                self.store(p, "spy_Sabotage", float(sabotaged) / float(len(suspects)))

        for leader, team in self.selections:
            suspects = [p for p in team if p in spies]
            if leader in spies:
                self.store(leader, "spy_PicksSpy", int(len(suspects) > 0))
                self.store(leader, "spy_PicksSelf", int(leader in team))
            else:
                self.store(leader, "res_PicksSpy", int(len(suspects) > 0))
                self.store(leader, "res_PicksSelf", int(leader in team))

        for votes, team in self.votes:
            spied = len([p for p in team if p in spies]) > 0
            for p, v in zip(self.players, votes):
                if spied:
                    if p in self.spies:
                        self.store(p, "spy_VotesForSpy", int(v))
                    else:
                        self.store(p, "res_VotesForSpy", int(v))
                else:
                    if p in self.spies:
                        self.store(p, "spy_VotesForRes", int(v))
                    else:
                        self.store(p, "res_VotesForRes", int(v))
        if LOG:
            console.log(self.global_statistics.__repr__())

    def _roulette(self, candidates):
        total = sum(c[1] for c in candidates)
        current = 0.0
        threshold = random.uniform(0.0, total)
        # console.log(candidates)
        for c in candidates:
            current += c[1]
            if current >= threshold:
                return c[0]
        return candidates[-1][0]

    def _estimate(self, player):
        return self.local_statistics[player].probability.estimate(
            self.number_of_players, self.spies_num
        )

    def store(self, player, attribute, value):
        self.global_statistics[player].__dict__[attribute].sample(value)

    def fetch(self, player, attributes):
        result = 0.0
        for a in attributes:
            result += (
                self.global_statistics[player]
                .__dict__[a]
                .estimate(self.number_of_players, self.spies_num)
            )
        return result / float(len(attributes))
