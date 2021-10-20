from agent import Agent


class MyAgent(Agent):
    """
    new_game and *_outcome methods simply inform agents of events that have occured,
    while propose_mission, vote, and betray require the agent to commit some action.
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
        self.number_of_players: int = 0
        self.player_number: int = -1
        self.spy_list: list[int] = []
        self.spy: bool = False
        self.spies_num: int = 0
        self.total_mission: int = 0
        self.failed_missions: int = 0
        self.successful_missions: int = 0

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
        self.number_of_players = number_of_players
        self.player_number = player_number
        self.spy_list = spy_list
        self.spy = bool(spy_list)
        self.spies_num = self.spy_count[number_of_players]
        self.total_mission = 0
        self.failed_missions = 0
        self.successful_missions = 0

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
        return []

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
        return False

    def vote_outcome(
        self, mission: list[int], leader: int, votes: dict[int, bool]
    ) -> None:
        """
        The method is called on an agent to inform them of the outcome of a vote,
        and which agent voted for or against the mission.

        Args:
            mission (list[int]):
                A list of unique agents to be sent on a mission.
            leader (int):
                The index of the player who proposed the mission
                between 0 and number_of_players.
            votes (dict[int, bool]):
                A dictionary mapping player indexes to Booleans.
                True if they voted for the mission, False otherwise.
        """
        pass

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
        return False

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
        pass

    def round_outcome(self, rounds_complete: int, missions_failed: int) -> None:
        """
        Informs all agents of the game state at the end of the round.

        Args:
            rounds_complete (int):
                The number of rounds (0-5) that have been completed.
            missions_failed (int):
                The number of missions (0-3) that have failed.
        """
        pass

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

        pass
