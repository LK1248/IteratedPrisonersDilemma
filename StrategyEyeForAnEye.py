import numpy as np
import random
import numpy as np
from StrategyBase import StrategyBase


class StrategyEyeForAnEye(StrategyBase):


    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.description = "Strategy - Eye for an eye - repeats the opponent's previous move"

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

