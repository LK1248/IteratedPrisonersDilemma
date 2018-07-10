import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import plot, draw, show

from copy import copy
from Player import Player
import numpy.matlib as ml

class Game:

    def __init__(self, RM, players_list, land_harvest_rate, max_plays_per_generation=np.inf, show_output = True):

        # Game holds:
        #
        # members:
        #     RM (rewards matrix) - 2x2
        #     land_harvest_rate
        #     active_players (list - external input)
        #     dead_players (list - generated during the game)

        self.RM                         = RM
        self.active_players             = players_list
        self.dead_players               = []
        self.land_harvest_rate          = land_harvest_rate
        self.play_pairs                 = []
        self.max_plays_per_generation   = max_plays_per_generation
        self.show_output                = show_output

        self.graphics                   = {}

        self.current_generation         = 0

        self.decision_names = ['Betray', 'Cooperate']

    # methods:
    # # Game repeats the: [Pair, Play(w/ instant thresholds), harvest+eat, update (w/ regular thresholds), move] sequence until:

    def add_new_player(self, player):
        # Adds a player to the players list. Will be called from either play_all_pairs or die_and_spawn
        if player.is_alive():
            self.active_players.append(player)

    def mark_player_dead(self, player):
        #         pops player out of the players list (will players.pop(player) work? We'll see) and add it to the dead_players list
        if not player.is_alive():
            dead_player = self.active_players.pop(self.active_players.index(player))
            self.dead_players.append(dead_player)
        else:
            raise ValueError("Player is not dead - only dead players should be moved to the dead_players list")
        return 1

    def get_number_of_active_players(self):
        return len(self.active_players)

    def build_pairs(self):
        # Build a list of play pairings, subject to:
        # 1. Both players are within each other's effective radius (i.e. they both see each other)
        # 2. No individual player can be in more than self.max_plays_per_generation pairs TODO: still not implemented

        # Build initial list of play pairings (all pairs that can see each other,
        # are not the same player, and are not already in the list)
        self.play_pairs = [(p1,p2,p1.distance_to_player(p2)) for p1 in self.active_players for p2 in self.active_players
                 if  p1 != p2
                 and p1.can_see_player(p2)
                 and p2.can_see_player(p1)
                 and (p2,p1,p2.distance_to_player(p1)) not in self.play_pairs]

        # Trim pairs, leaving only self.max_plays_per_generation pairs for each player (the ones nearest to the player)
        # Loop until all players have no more than self.max_plays_per_generation pairs
        trimmed_pairs = []
        for p in self.active_players:
            p_pairs = [pair for pair in self.play_pairs if pair[0]==p or pair[1]==p]
            if len(p_pairs)>self.max_plays_per_generation:
                p_pairs=sorted(p_pairs, key=lambda k:k[2])[:self.max_plays_per_generation]
            trimmed_pairs += p_pairs

        self.play_pairs = trimmed_pairs

        return 1

    def make_output_invisible(self):
        self.show_output = False

    def make_output_visible(self):
        self.show_output = True

    def handle_output(self, output_function):
        if self.show_output:
            output_function()


    def show_play(self, p1, p2, p1_decision, p2_decision):
        #     Displays (graphically?) a single game between 2 players
        p1_ID = p1.get_ID()
        p2_ID = p2.get_ID()
        p1_decision_name = self.decision_names[p1_decision]
        p2_decision_name = self.decision_names[p2_decision]

        out_str = f"Game between P1 (ID:{p1_ID}) and P2 (ID:{p2_ID})\n"
        out_str += f"Player1 (ID:{p1_ID}) chooses: {p1_decision_name}\n"
        out_str += f"Player2 (ID:{p2_ID}) chooses: {p2_decision_name}\n"

        out_fun = lambda : print(out_str)

        self.handle_output(out_fun)

    def play_all_pairs(self):
        for pair in self.play_pairs:
            p1 = pair[0]
            p2 = pair[1]

            # Get decisions from both players
            p1_decision = p1.play(p2.get_ID())
            p2_decision = p2.play(p1.get_ID())

            # Send decision to both players
            p1.update(opponent_ID=p2.get_ID(), my_decision=p1_decision, opponent_decision=p2_decision)
            p2.update(opponent_ID=p1.get_ID(), my_decision=p2_decision, opponent_decision=p1_decision)

            self.show_play(p1, p2, p1_decision, p2_decision)

    def get_visible_neighbors_of_player(self, player):
        visible_neighbors = [p for p in self.active_players if player.can_see_player(p) and player != p]
        return visible_neighbors

    def harvest_and_eat(self):
        # All players harvest food (proportional to effective radius, inversely proportional to number of visible neighbors)
        # All players feed (lower their current reward score)
        for player in self.active_players:
            num_of_visible_neighbors = len(self.get_visible_neighbors_of_player(player))
            harvest_area = np.pi * player.get_effective_radius() ** 2
            harvested_reward = self.land_harvest_rate *  harvest_area / (num_of_visible_neighbors+1)

            player.harvest(harvested_reward)
            # self.handle_output(f"player has {num_of_visible_neighbors} neighbors, harvests {harvested_reward}")
            player.feed()

    def die_and_spawn(self):
        # Check current reward vs. spawn / death thresholds for all players.
        active_players_list = copy(self.active_players)
        for player in active_players_list:
            result = player.check_thresholds()

            # If a new player is spawned, result will be a Player object
            if isinstance(result, Player):
                self.add_new_player(result)

            # If player dies from hunger, result will be 0
            elif result == 0:
                self.mark_player_dead(player)

            else:
                pass

    def move_players(self):
        for player in self.active_players:
            visible_neighbors = self.get_visible_neighbors_of_player(player)
            visible_locations = [p.get_location() for p in visible_neighbors] # Do I need np.array() for this?
            player.move(visible_locations)

    def current_population_size(self):
        return len(self.active_players)

    def run_one_generation(self):

        self.handle_output(lambda: print(f"\n**************\nGeneration #{self.current_generation}:\n**************\n"))

        # Run a full cycle of: Playing, harvesting/eating, dying/spawning, moving
        self.build_pairs()
        self.play_all_pairs()
        self.harvest_and_eat()
        self.die_and_spawn()
        self.move_players()

        self.current_generation += 1

        self.show_population()

        return self.current_population_size()


    def show_status_graphically(self):
        # Graphical representation - move this to a function

        if not self.graphics.get('fig',False):
            fig = plt.figure()
            ax = fig.add_axes([0.1, 0.1, 0.8, 0.6])
            show(block=False)
            self.graphics['fig'] = fig
            self.graphics['ax'] = ax

        fig = self.graphics['fig']
        ax = self.graphics['ax']
        ax.cla()

        marker_list = ['d', '+', 'o', '.', 's']
        edge_color_list = ['b', 'r', 'g', 'y', 'k', 'c']

        population_IDs = [p.get_ID() for p in self.active_players]
        unique_IDs = list(set(population_IDs))

        sample_player_with_this_ID = {}
        number_of_players_with_this_ID = {}
        for ID in unique_IDs:
            players_with_this_ID = [p for p in self.active_players if p.get_ID() == ID]
            sample_player_with_this_ID[ID] = players_with_this_ID[0]
            number_of_players_with_this_ID[ID] = len(players_with_this_ID)
            locations = np.array([p.get_location() for p in players_with_this_ID])
            rewards = [p.get_current_reward() for p in players_with_this_ID]
            marker_list_ID = ID % len(marker_list)
            ax.scatter(x=locations[:, 0],
                       y=locations[:, 1],
                       s=rewards * 10,
                       marker=marker_list[marker_list_ID],
                       alpha=0.3,
                       edgecolors=edge_color_list[marker_list_ID],
                       )

        ax.set_xlim([-10,10])
        ax.set_ylim([-10,10])
        ax.set_title(f"Generation #{self.current_generation}")


        leg_str = [f"{number_of_players_with_this_ID[ID]} - {sample_player_with_this_ID[ID].strategy.get_description()}" for ID in unique_IDs]
        ax.legend(leg_str, loc='upper center', bbox_to_anchor=(0.5, 1.45),
          ncol=1, fancybox=True, shadow=True)

        plt.pause(0.1)


    def show_population(self):
        #     show_population()
        #         w/o graphics: a sorted list (descending, sorted by # of players) of: [ID, #of players]
        #         with graphics:
        #             dead players are a grey circle
        #             living players are a colored, filled circle with color matching the ID (somehow)
        #             radius is proportional to current reward. Inversely proportional to total number of players
        #                 consider: radius = current_reward / sum(all_active_player_rewards)
        #
        total_num_of_players = self.current_population_size()
        population_IDs = [p.get_ID() for p in self.active_players]
        unique_IDs = list(set(population_IDs))
        population_count = [(ID,population_IDs.count(ID)) for ID in unique_IDs]
        out_fun = lambda : print(population_count)
        self.handle_output(out_fun)


        self.show_status_graphically()





        if total_num_of_players:
            return population_count
        else:
            return 0

