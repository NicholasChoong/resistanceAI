from .agent import Agent
import math, random
from itertools import combinations
import collections

# add confirm spy and resistance list ()
class BayeBehaviourAgent(Agent):
    def __init__(self, name="22412148"):
        self.name = name

    def new_game(self, number_of_players, player_number, spies):
        self.number_of_players = number_of_players
        self.player_number = player_number
        self.all_spies = []
        self.other_spies = []
        self.spy_rating = []
        self.spy = False

        self.confirm_spies = []
        self.confirm_resistance = []

        self.player_info = {}

        self.number_of_spies = self.spy_count[self.number_of_players]
        self.number_of_resistance = self.number_of_players - self.number_of_spies

        # print("AI PLAYER NUMBER IS: " + str(self.player_number))

        self.assistedSpies_WEIGHT = 0.1
        self.spyBehaviour_WEIGHT = 0.2
        self.resistanceBehaviour_WEIGHT = 0.05

        for i in range(self.number_of_players):
            if i != self.player_number:
                self.player_info[i] = {
                    "assistedSpies": 0,
                    "spyBehaviour": 0,
                    "resistanceBehaviour": 0,
                }
                # To retrieve information: self.player_info[playernumber]["helpledSpies"]
                # To be used as a counter for calculation counter of 2: 1+(1.25*0.25)*spyprobability, 3: 1+(1.25*1.25*0.25)*spyprobability
                # Reset counter after every mission

        # Check if spies is empty, if so, agent is resistance, otheriwse, spy
        if not spies:
            self.spy = False

            # print("AI AGENT IS NOT SPY")

            initial_prob = 1.00 / (self.number_of_players - 1)

            for i in range(self.number_of_players):
                if i != self.player_number:
                    self.spy_rating.append(initial_prob)
                # 0 for self when not a spy
                else:
                    self.spy_rating.append(0.0)

            # print('PROBABILITIES OF PLAYERS: ')
            # print(self.spy_rating)

            # assistedSpies           assisted the spy team; voted for failed missions                                                            1+0.25   how much influence this behaviour
            # spyBehaviour            general suspicious behaviour; votes no on the team they are not in when mission size = number of resistance 1+0.50   should have on the spyness
            # resistanceBehaviour     vote against a team they themselves are on                                                                  1-0.1

        else:
            self.spy = True

            # print("AI AGENT IS A SPY")
            """
            for player in range(self.number_of_players):
                if player in spies:
                    self.spy_rating.append(1)
                else:
                    self.spy_rating.append(0)
            """
            # update spy ratings in a resistance perspective
            initial_prob = 1.00 / (self.number_of_players - 1)

            for i in range(self.number_of_players):
                if i != self.player_number:
                    self.spy_rating.append(initial_prob)
                # 0 for self when not a spy
                else:
                    self.spy_rating.append(0.0)

            for player in spies:
                if player != self.player_number:
                    self.other_spies.append(player)
                self.all_spies.append(player)

            # print("OTHER SPIES ARE: " + str(self.other_spies))
            # print("ALL SPIES ARE: " + str(self.all_spies))

        self.mission_votes = {}

        self.round_number = 1
        self.current_fails = 0
        self.proposal_number = 1
        self.betrays_required = self.fails_required[self.number_of_players][
            self.round_number - 1
        ]

        self.missionCombination = []
        self.non_missionCombination = []

    def propose_mission(self, team_size, betrayals_required=1):
        team = []

        if self.spy and self.betrays_required > 1:
            team.append(self.player_number)
            ref_list = self.other_spies.copy()

            for i in range(self.betrays_required - 1):
                random_spy = random.choice(ref_list)
                if random_spy not in team:
                    team.append(random_spy)
                    ref_list.remove(random_spy)

            team = self._choose_team(team, team_size, self.spy, self.confirm_resistance, self.confirm_spies)

        elif self.spy:
            team.append(self.player_number)
            team = self._choose_team(team, team_size, self.spy, self.confirm_resistance, self.confirm_spies)

        elif not self.spy and self.round_number == 1:
            team.append(self.player_number)
            ref_list = [] 
            
            for p in range(self.number_of_players):
                if p != self.player_number:
                    ref_list.append(p)
            
            while len(team) < team_size:
                random_agent = random.choice(ref_list)
                team.append(random_agent)
                ref_list.remove(random_agent)

        else:
            team = self._choose_team(team, team_size, self.spy, self.confirm_resistance, self.confirm_spies)

        return team

    def vote(self, mission, proposer):

        # always allow first misson and the fifth mission proposal to go through
        if self.round_number == 1 or self.proposal_number == 5:
            return True

        # team leader or member has high proabability of being a spy then vote no
        if self.spy:
            # Find the number spies within the mission
            spies_in_mission = self._spies_in_mission(mission, self.all_spies)

            # Check if agent is in mission, if so accept mission
            if proposer == self.player_number or self.player_number in mission:
                return True
            # If spies only need 1 more win and we have enough spies in the mission, accept the mission
            elif self.current_fails == 2 and spies_in_mission >= self.betrays_required:
                return True
            else:
                return bool(
                    len([s for s in mission if s in self.other_spies])
                    >= self.betrays_required
                )
        else:
            sortedProb = self.spy_rating.copy()
            sortedProb.sort()
            idealRating = 0.0
            missionRating = 0.0
            # print("Sorted probability list is: " + str(sortedProb))
            if proposer in self.confirm_spies:
                return False

            for p in mission:
                if p in self.confirm_spies:
                    return False

            for p in self.confirm_resistance:
                if p not in mission:
                    return False

            # Always reject if one more mission left for spies to win, but resistance agent not in mission
            if self.current_fails >= 2 and self.player_number not in mission:
                return False

            for i in range(len(mission)):
                idealRating += sortedProb[i]
            # print("Min prob for mission is: " + str(idealRating))

            for player in mission:
                missionRating += self.spy_rating[player]
            # print("Mission probability is: " + str(missionRating))

            # If ideal team with added leeway is selected, accept the mission, if not, reject mission
            return [True if missionRating < idealRating + (idealRating / 10) else False]

    def vote_outcome(self, mission, proposer, votes):
        required_votes = self.number_of_players / 2
        success = bool(len(votes) > required_votes)
        mission_size = self.mission_sizes[self.number_of_players][self.round_number - 1]

        ideal_team = self._choose_team([], mission_size, self.spy, self.confirm_resistance, self.confirm_spies)

        # If mission was voted for, add it into the array
        if success:
            self.mission_votes[self.round_number] = proposer, mission, votes

            # print("PROPOSER WAS: " + str(proposer))
            # print("MISSON VOTES: " + str(self.mission_votes))

            if collections.Counter(mission) == collections.Counter(ideal_team):
                for player in range(self.number_of_players):
                    if player != self.player_number and player not in votes:
                        self.player_info[player][
                            "resistanceBehaviour"
                        ] += 1  # COUNTER HERE

        # If mission was voted off, increment proposal number
        # If the mission could have been successful, but was voted off, increase suspicion levels
        else:
            self.proposal_number += 1

            if self.round_number == 1:
                # increase suspicion levels for people that rejected first mission
                for player in range(self.number_of_players):
                    if player not in votes and player != self.player_number:
                        self.player_info[player]["spyBehaviour"] += 1
            else:
                if collections.Counter(mission) == collections.Counter(ideal_team):
                    for player in range(self.number_of_players):
                        if player != self.player_number and player not in votes:
                            self.player_info[player][
                                "spyBehaviour"
                            ] += 1  # COUNTER HERE

        # Other behavioural checks
        for voter in votes:
            if voter == self.player_number:
                continue  # Skip if myself
            if voter not in mission and len(mission) == self.number_of_resistance:
                # They are suspicious because they are voting for a mission they are not in when team members = resistance number
                self.player_info[voter]["spyBehaviour"] += 1  # COUNTER HERE

        for player in mission:
            if player == self.player_number:
                continue  # Skip if myself
            if player not in votes:
                # Voting against mission when they are on it may be resistance like
                self.player_info[player]["resistanceBehaviour"] += 1  # COUNTER HERE

    def betray(self, mission, proposer):
        # When not a spy, never betray (precautionary check)
        if not self.spy:
            return False

        spy_num = self._spies_in_mission(mission, self.all_spies)

        # print("\nMISSION PLAYERS: " + str(mission))
        # print("NUMBER OF SPIES IN MISSION: " + str(spy_num))
        # print("MISSION LEADER: " + str(proposer))
        # print("FAILS REQUIRED: " + str(self.betrays_required))

        # When a spy, check for other spies on mission and number of people on the mission
        # If there are less spies in the mission than required, don't betray to look innocent
        # as there is no point in betraying when you can't fail the mission
        if spy_num < self.betrays_required:
            return False

        # There are enough spies on mission and only need 1 more to win then betray
        if self.current_fails == 2:
            return True

        # Betray the mission if you must fail 2 missions in a row to win
        if self.current_fails == 1 and self.round_number == 4:
            return True

        # If just enough spies are on mission and it's not the first round then betray
        if spy_num == self.betrays_required and self.round_number != 1:
            return True

        # If there are more than enough spies on the mission to fail it, betray with probability
        if spy_num > self.betrays_required:
            idealRating = 0.80  # Must be at least 80% confident that other spies will betray to not betray

            missionRating = (
                float(spy_num / self.betrays_required) * 0.70
            )  # Assuming spies will betray 70% of the time

            return [False if missionRating > idealRating else True]

        return True

    def mission_outcome(self, mission, proposer, num_fails, mission_success):
        # No betrayals occurred, mission successful
        if num_fails == 0:
            for p in range(self.number_of_players):
                if (
                    p == self.player_number
                ):  # Skip yourself because there's no need to update your own info
                    continue
                # Check if player voted yes for the mission
                if (
                    p in self.mission_votes[self.round_number][2]
                    and self.round_number != 1
                    and p
                ):
                    # self.spy_rating[p] -= 0 # a certain value
                    # self._update_ratings(mission, num_fails)
                    self.player_info[p]["resistanceBehaviour"] += 1
                elif (
                    p not in self.mission_votes[self.round_number][2]
                    and self.round_number != 1
                ):
                    # self._update_ratings(mission, num_fails)
                    # self.spy_rating[p] += 0 # a certain value
                    self.player_info[p]["assistedSpies"] += 1
                else:  # First round mission outcome
                    if p in mission or p in self.mission_votes[self.round_number][2]:
                        self.player_info[p]["resistanceBehaviour"] += 1
                    else:
                        self.player_info[p]["assistedSpies"] += 1

        # There were betrayal(s) but mission was still successful
        # A little tricky because spies may reject due to insiffucient spies in mission
        elif num_fails > 0 and mission_success:
            for p in range(self.number_of_players):
                if p in self.mission_votes[self.round_number][2]:
                    # self.spy_rating[p] += 0 # a certain value
                    self._update_ratings(mission, num_fails)

                else:
                    self._update_ratings(mission, num_fails)
                    # self.spy_rating[p] -= 0 # a certain value

        # Mission failed
        else:
            # All players that were not in the mission are clear when number of fails = number of spies
            if num_fails == self.spy_count[self.number_of_players]:
                remainRating = 0.0

                for p in range(self.number_of_players):
                    if p not in mission and p != self.player_number:
                        remainRating += self.spy_rating[p]
                        self.spy_rating[p] = 0.0
                        self.confirm_resistance.append(p)

                for p in range(self.number_of_players):
                    addProb = float(remainRating / len(mission))
                    if (
                        p in mission
                        and self.spy_rating[p] > 0
                        and p != self.player_number
                    ):
                        self.spy_rating[p] += addProb

            elif num_fails == len(mission):
                for p in mission:
                    self.spy_rating[p] += 1000.0
                    self.confirm_spies.append(p)
                for p in range(self.number_of_players):
                    if (
                        p in self.mission_votes[self.round_number][2]
                        and p not in mission
                        and p != self.player_number
                    ):
                        self.player_info[p]["assistedSpies"] += 1  # COUNTER HERE

            # There were less fails than total spies, spies could have not betrayed or was not in mission
            else:
                self._update_ratings(mission, num_fails)
                for p in range(self.number_of_players):
                    if (
                        p in self.mission_votes[self.round_number][2]
                        and p != self.player_number
                    ):
                        self.player_info[p]["assistedSpies"] += 1

    def round_outcome(self, rounds_complete, missions_failed):
        """
        basic informative function, where the parameters indicate:
        rounds_complete, the number of rounds (0-5) that have been completed
        missions_failed, the numbe of missions (0-3) that have failed.
        """

        # Update internal variables
        self.round_number = rounds_complete + 1
        self.current_fails = missions_failed
        if self.round_number <= 5:
            self.betrays_required = self.fails_required[self.number_of_players][
                self.round_number - 1
            ]

        # Reset proposal mission number
        self.proposal_number = 1

        # Apply behavioural weights to probabilities and reset dictionary at the end of every mission
        self._behavioural_update()

    def game_outcome(self, spies_win, spies):
        # Nothing to do unless a multi-game learning agent

        """
        basic informative function, where the parameters indicate:
        spies_win, True iff the spies caused 3+ missions to fail
        spies, a list of the player indexes for the spies.
        """
        self._get_sus_players()

    def _get_sus_players(self):
        sus_players = {}

        for player in range(self.number_of_players):
            sus_player[player] = self.spy_rating[player]

        return sus_players

    # Pick people with lowest probability of being a spy
    def _choose_team(self, current_team, team_size, is_spy, include, exclude):
        team = current_team.copy()
        # print("CURRENT TEAM: " + str(team))

        if include:
            for p in include:
                if p not in team and len(team) < team_size:
                    team.append(p)

        if not is_spy:
            while len(team) < team_size:
                ref = math.inf
                player = self.player_number

                # Use of index counter because different agents can have the same probability
                # which will cause errors when using the index() function
                index = 0

                for prob in self.spy_rating:
                    if prob < ref and index not in team and index not in exclude:
                        ref = prob
                        player = index

                    index += 1

                team.append(player)
            # print("FINAL TEAM: " + str(team))

        else:
            while len(team) < team_size:
                ref = math.inf
                player = self.player_number

                # Use of index counter because different agents can have the same probability
                # which will cause errors when using the index() function
                index = 0

                for prob in self.spy_rating:
                    if prob < ref and index not in team and index not in self.all_spies:
                        ref = prob
                        player = index

                    index += 1

                team.append(player)
        return team

    def _spies_in_mission(self, mission, spies):
        total = 0

        for player in mission:
            if player in spies:
                total += 1

        return total

    def _combination_calc(self, mission, size):
        combos = list(combinations(mission, size))
        return combos

    def _rating_calc(self, mission, combos):
        pB = 0.0
        for combo in combos:
            pB = 0.0
            pBk = 1.0
            non_combo = []

            for player in mission:
                if player not in combo:
                    non_combo.append(player)

            # non_combo = set(mission) - set(combo)

            for player in combo:
                pBk *= self.spy_rating[player]

            for player in non_combo:
                pBk *= 1 - self.spy_rating[player]

            pB += pBk

        if not pB:
            return 1.0

        return pB

        """
        pA = probability A is a spy
        pB = probability of getting a mission outcome with a team
        pBa = probability of getting the mission outcome assuming A is a spy
        pAb = the probability a is a spy given the mission
        """

    def _baye_calculation(self, pA, pB, pBa):
        if not pB:
            return pB
        else:
            result = (pBa * pA) / pB
            return result

    def _update_ratings(self, mission, fails_occurred):
        pA = 0.0
        pB = 0.0
        pAb = 0.0
        pBa = 0.0

        self.missionCombination.clear()
        self.non_missionCombination.clear()

        not_in_mission = []
        for player in range(self.number_of_players):
            if player not in mission:
                not_in_mission.append(player)

        self.missionCombination = self._combination_calc(mission, fails_occurred)
        # print("REMAINING SPIES: " + str(self.number_of_spies) + '-' + str(fails_occurred) + str(self.number_of_spies-fails_occurred))
        self.non_missionCombination = self._combination_calc(
            not_in_mission, (self.number_of_spies + 1 - fails_occurred)
        )

        # Calculate P(A|B) for each player: probability of them being a spy given the last mission
        for player in range(self.number_of_players):
            pA = self.spy_rating[player]
            ref = []

            if player in mission:
                other_members = [i for i in mission if i != player]
                # print("MISSION: " + str(mission))
                # print("OTHER MEMBERS: " + str(other_members))
                ref.append(other_members)

                pB = self._rating_calc(mission, self.missionCombination)
                pBa = self._rating_calc(mission, ref)

            else:
                other_members = [i for i in not_in_mission if i != player]
                # print("NOT ON MISSION: " + str(other_members))
                ref.append(other_members)

                pB = self._rating_calc(not_in_mission, ref)
                pBa = self._rating_calc(not_in_mission, ref)

            # print("pA = " +str(pA) +" pB = " +str(pB)+ " pBa = " + str(pBa))
            pAb = self._baye_calculation(pA, pB, pBa)
            # print("PROBABILITY CHANGED FROM: " + str(self.spy_rating[player]) + " TO: " + str(pAb) + " FOR AGENT: " + str(player))
            self.spy_rating[player] = pAb

    def _behavioural_update(self):
        influence = 0.0

        player_list = [
            p for p in range(self.number_of_players) if p != self.player_number
        ]
        for p in player_list:
            spy_assists = self.player_info[p]["assistedSpies"]
            if spy_assists > 1:
                influence = (
                    pow((1 + self.assistedSpies_WEIGHT), spy_assists - 1)
                    * self.assistedSpies_WEIGHT
                ) + 1
                self.spy_rating[p] *= influence
                self.player_info[p]["assistedSpies"] = 0
                # print("Spy assist influence: " + str(influence) + " for player: " + str(p))

            elif spy_assists == 1:
                influence = self.assistedSpies_WEIGHT + 1
                self.spy_rating[p] *= influence
                self.player_info[p]["assistedSpies"] = 0
                # print("Spy assist influence: " + str(influence) + " for player: " + str(p))

            spy_actions = self.player_info[p]["spyBehaviour"]
            if spy_actions > 1:
                influence = (
                    pow((1 + self.spyBehaviour_WEIGHT), spy_actions - 1)
                    * self.spyBehaviour_WEIGHT
                ) + 1
                self.spy_rating[p] *= influence
                self.player_info[p]["spyBehaviour"] = 0
                # print("Spy behaviour influence: " + str(influence) + " for player: " + str(p))

            elif spy_actions == 1:
                influence = self.spyBehaviour_WEIGHT + 1
                self.spy_rating[p] *= influence
                self.player_info[p]["spyBehaviour"] = 0
                # print("Spy behaviour influence: " + str(influence) + " for player: " + str(p))

            resistance_actions = self.player_info[p]["resistanceBehaviour"]
            if resistance_actions > 1:
                influence = 1 - (
                    pow((1 + self.resistanceBehaviour_WEIGHT), resistance_actions - 1)
                    * self.resistanceBehaviour_WEIGHT
                )
                self.spy_rating[p] *= influence
                self.player_info[p]["resistanceBehaviour"] = 0
                # print("Resistance behaviour influence: " + str(influence) + " for player: " + str(p))

            elif resistance_actions == 1:
                influence = 1 - self.resistanceBehaviour_WEIGHT
                self.spy_rating[p] *= influence
                self.player_info[p]["resistanceBehaviour"] = 0
                # print("Resistance behaviour influence: " + str(influence) + " for player: " + str(p))
