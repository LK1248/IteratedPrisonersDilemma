import numpy as np
import random
import numpy as np
import move_strategies

from StrategyBase import StrategyBase


class StrategySaint(StrategyBase):


    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.description = "Saint - always choose cooperate"

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
        return 1

    # CORE COMPONENT - how the state is updated after both players have played. Returns the updated state
    def update_state(self, state, opponent_ID, my_decision, opponent_decision, my_game_state):
        return opponent_decision


    # CORE COMPONENT - how the location is updated based on all neighbors in the effective range. Returns the updated location
    def move_to_new_location(self, location, visible_neighbor_locations, effective_radius=np.inf):
        return move_strategies.push_model(location, visible_neighbor_locations)
        # return move_strategies.push_and_pull_model(location, visible_neighbor_locations)
        # return move_strategies.move_towards_all_other_players(location, visible_neighbor_locations)

############################################################################
########################## CORE COMPONENTS #################################
############################################################################

