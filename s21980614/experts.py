from .agent import Agent
import itertools
import random
from rich.console import Console
from rich.traceback import install

console = Console()
install(show_locals=True)

LOG = False


def permutations(config):
    """Returns unique elements from a list of permutations."""
    return list(set(itertools.permutations(config)))


class ExpertAgent(Agent):
    """Simplification of Invalidator, one of the strongest AIs against bots from
    the 2012 competition.
    @name: Invalidator Bot
    @author: Alex J. Champandard <alexjc@aigamedev.com>
    @license: GNU Public License (GPL) version 3.0
    @about: THE RESISTANCE Competition, Vienna Game/AI Conference 2012.
    @since: 01.06.2012
    """

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
        self.spies: list[int] = spy_list
        self.spy = bool(spy_list)
        self.players: list[int] = list(range(number_of_players))
        self.spies_num: int = self.spy_count[number_of_players]
        self.number_of_rounds_on_mission: int = 0
        self.total_mission: int = 0
        self.failed_missions: int = 0
        self.successful_missions: int = 0

        self.team: list[int] = []
        self.leader: int = -1

        # Count the number of times each configuration was apparently invalidated.
        self.invalidations = {k: 0.0 for k in permutations([True, True, False, False])}
        # This is used to help justify decisions in hybrid human/bot matches.
        self.factors = {k: [] for k in permutations([True, True, False, False])}

    if __name__ == "__main__":
        console.log(permutations([True, True, False, False]))

    def is_spy(self):
        """
        returns True iff the agent is a spy
        """
        return self.player_number in self.spies

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
        likely = self.likeliest()
        config = random.choice(likely)
        return [self.player_number] + random.sample(
            self.getResistance(config), team_size - 1
        )

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
        self.team = mission
        self.leader = leader
        advice = self.adviser_vote(mission)
        if advice:
            return advice

        # Count the scores of configurations where no spies are selected.
        scores, matches = [], []
        for config in self.invalidations:
            if len([s for s in mission if s in self.getSpies(config)]) == 0:
                scores.append(self.invalidations[config])
                matches.append(config)
        if not scores:
            return False

        # Establish whether this meets the criteria for selection...
        threshold = min(self.invalidations.values())
        return min(scores) <= threshold

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
        self.team = mission
        self.leader = leader
        for config in self.invalidations:
            score, factors = self.oracle_voting(config, votes)
            self.invalidations[config] += score
            self.factors[config].extend(factors)

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
        if self.successful_missions == 2 or self.failed_missions == 2:
            # self.log.debug("Sabotaging since there's a chance of winning or losing.")
            return True

        if len(self.team) == 2:
            # self.log.debug("Missions of size two are too risky...")
            return False

        spies = [s for s in self.team if s in self.spies]
        if len(spies) > 1:
            # self.log.debug("Too many spies, can't coordinate!")
            return False

        # self.log.debug("Other checks failed, why not sabotage since I'm a spy?")
        return True

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
        if mission_success:
            self.successful_missions += 1
        sabotaged = 0 if mission_success else 1
        for config in self.invalidations:
            score, factors = self.oracle_sabotages(config, sabotaged)
            self.invalidations[config] += score
            self.factors[config].extend(factors)

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
        sorted_dict = {
            k: v
            for k, v in sorted(self.invalidations.items(), key=lambda item: item[1])
        }
        if LOG and not self.spy:
            console.log(list(sorted_dict.items())[-1])
            console.log(spies)

    def oracle_selection(self, config):
        """Rate teams chosen by the leader, assuming a particular configuration.
        Zero means the selection is not suspicious, and positive values indicate
        higher suspicion levels."""

        all_spies = self.getSpies(config)
        team_spies = [s for s in self.team if s in all_spies]
        if self.leader in all_spies and len(team_spies) == 0:
            return 1.0, [
                (1.0, "%s, assuming a spy, did not pick a mission with spies.")
            ]
        if len(team_spies) >= 2:
            return 0.5, [(0.5, "%s, assuming a spy, picked a mission with two spies!")]
        return 0.0, []

    def oracle_voting(self, config, votes):
        """Assess the votes of a player, assuming a particular configuration.
        Zero means no suspicious activity and positive values indicate high
        suspicion levels."""

        all_spies = self.getSpies(config)
        team_spies = [s for s in self.team if s in all_spies]

        score, factors = 0.0, []
        for p, v in zip(self.players, votes):
            if p in all_spies and v and not team_spies:
                score += 1.0
                factors.append(
                    (
                        1.0,
                        "%s, assuming a spy, voted for a mission that had no assumed spies."
                        % (p),
                    )
                )
            if p in all_spies and not v and len(team_spies) == 1:
                score += 1.0
                factors.append(
                    (
                        1.0,
                        "%s, assuming a spy, did not vote a mission that had an assumed spy."
                        % (p),
                    )
                )
            if p in all_spies and v and len(team_spies) > 1:
                score += 0.5
                factors.append(
                    (
                        0.5,
                        "%s, assuming a spy, voted a mission with multiple assumed spy."
                        % (p),
                    )
                )
            if self.number_of_rounds_on_mission == 5 and p not in all_spies and not v:
                score += 2.0
                factors.append(
                    (
                        2.0,
                        "%s, assuming resistance, did not approve the final try!" % (p),
                    )
                )
            if p not in all_spies and len(self.team) == 3 and p not in self.team and v:
                score += 2.0
                factors.append(
                    (
                        2.0,
                        "%s, assuming a resistance, voted for a mission without self!"
                        % (p),
                    )
                )
        return score, factors

    def oracle_sabotages(self, config, sabotaged):
        spies = [s for s in self.team if s in self.getSpies(config)]
        score = max(0, sabotaged - len(spies)) * 100.0
        if score > 0.0:
            return score, [
                (
                    score,
                    "%s participated in a mission that had %i sabotages."
                    % (self.team, sabotaged),
                )
            ]
        else:
            return 0.0, []

    def adviser_vote(self, team):
        if self.spy:
            spies = [s for s in team if s in self.spies]
            if len(spies) > 0 and (
                self.failed_missions == 2 or self.successful_missions == 2
            ):
                # self.log.debug("Taking a risk since the game could finish.")
                return True
            if self.number_of_rounds_on_mission == 5:
                # self.log.debug("Voting up the last mission because Resistance would.")
                return False
            if len(team) == 3:
                # self.log.debug("Voting strongly about this team because it's size 3!")
                return self in team
        else:
            if self.leader == self:
                # self.log.debug("Approving my own mission selection.")
                return True
            if self.number_of_rounds_on_mission == 5:
                # self.log.debug("Voting up the last mission to avoid failure.")
                return True
        return None

    def likeliest(self):
        ranked = sorted(self.invalidations.keys(), key=lambda c: self.invalidations[c])
        invalidations = self.invalidations[ranked[0]]
        return [r for r in ranked if self.invalidations[r] == invalidations]

    def getSpies(self, config):
        assert len(config) == 4
        assert all([type(c) is bool for c in config])
        return set([player for player, spy in zip(self.others(), config) if spy])

    def getResistance(self, config):
        assert len(config) == 4
        assert all([type(c) is bool for c in config])
        return set([player for player, spy in zip(self.others(), config) if not spy])

    def others(self):
        """Helper function to list players in the game that are not your bot."""
        return [p for p in self.players if p != self.player_number]
