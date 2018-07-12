import numpy as np
from Player import Player
import random
import move_strategies


class StrategyBase:
#    Strategy
#        Note: This defines a parent class. Specific strategies will have specific sub-classes.
#        The Basic class implements the Eye-For-an-Eye strategy
#
#        members:
#            my_ID: ID of player using this strategy
#            states: dictionary with [player IDs] as keys, and a state for each key
#            description


    def __init__(self,
                    ID               = None,
                    private_ID       = None,
                    RM               = [[0,0],[0,0]],
                    location         = np.array([0,0]),
                    effective_radius = np.inf,
                    description      = 'Basic strategy'):
        self.my_ID              = ID
        self.my_private_ID      = private_ID
        self.RM                 = RM
        self.my_location        = location
        self.effective_radius   = effective_radius
        self.description        = description

        self.init_self_ID_state() # Initialize the "states" member using the same ID as this object.


############################################################################
########################## CORE COMPONENTS #################################
############################################################################

    # CORE COMPONENT - initial state vs. new opponent. Returns initial state
    def init_state(self):
        # Creates a new state. Will be attached to a new ID
        return 1

    # CORE COMPONENT - how the state affects the decision. Returns decision
    def get_decision_from_state(self, state, my_game_state):
        # get_decision(state):
        #     Core decision function. Uses current opponent state to decide action
        return state

    # CORE COMPONENT - how the state is updated after both players have played. Returns the updated state
    def update_state(self, state, opponent_ID, my_decision, opponent_decision, my_game_state):
        return opponent_decision


    # CORE COMPONENT - how the location is updated based on all neighbors in the effective range. Returns the updated location
    def move_to_new_location(self, location, visible_neighbor_locations):

        num_of_neighbors = len(visible_neighbor_locations)

        if num_of_neighbors == 0:
            new_location = location
        else:
            neighbors_cm = sum(visible_neighbor_locations)/num_of_neighbors
            d = location - neighbors_cm
            new_location = location + 0.1*d # Move away from neighbors

        return new_location

############################################################################
########################## CORE COMPONENTS #################################
############################################################################

    def get_description(self):
        return self.description

    def init_self_ID_state(self):
        # init_self_ID_state(): create a new state for the player's ID
        states = {self.my_private_ID : self.init_state()}
        self.states = states

    def add_new_ID(self,ID):
        # add_new_ID(ID): create a new state for key [ID],
        new_state = self.init_state()
        self.states[ID] = new_state

    def play(self, opponent_ID, my_game_state):
        # play:
        #     input: opponent's ID
        #     output: decision (0=betray, 1=cooperate)
        #
        #     If ID does not exist, add_new_ID(ID).
        #     return get_decision(ID)
        #     Note: for now, play() should NOT alter the state. Only update() will do that
        known_IDs = self.states.keys()
        if opponent_ID not in known_IDs:
            self.add_new_ID(opponent_ID)
        return self.get_decision(opponent_ID, my_game_state)

    def get_decision(self, ID, my_game_state):
        state = self.states[ID]
        return self.get_decision_from_state(state, my_game_state)

    def update(self, opponent_ID, my_decision, opponent_decision, my_game_state):
        # update:
        #     input: opponent's ID, player's decision, opponent's decision
        #     output: None
        #     updates states[ID] per match inputs and result
        state = self.states[opponent_ID]
        state = self.update_state(state, opponent_ID, my_decision, opponent_decision, my_game_state)
        self.states[opponent_ID] = state


    def move(self, game_state, visible_neighbor_locations):
        # move():
        #     input:
        #         neighbors_list - list of {'location': loc, 'ID': ID} pairs for all neighbors within effective_radius
        #     process:
        #         update location based on neighbors_list
        #     output:
        #         returns new location



        location = game_state['location']

        new_location = self.move_to_new_location(location, visible_neighbor_locations)
        return new_location