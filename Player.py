import numpy as np
from copy import copy, deepcopy
import move_strategies

class Player:

    # members:
    #
    # ID
    # is_alive
    # PD rewards matrix (inits from Game. Ideally equal in all players but not necessarily)
    # reward score (inits to a value defined by TBD)
    # location (x,y) - in [0,1]x[0,1]
    # thresholds for death / spawn / instant_death=-INF / instant_spawn=INF
    # effective_radius (controls sight around player, and harvest range. Maybe something like 2*pi*R^2=0.01 --> R==sqrt(0.01/2pi))
    # food_requirement
    #
    # movement+play strategy (which can hold state) - object of class strategy_class (created during init)

    def __init__(self,  ID,
                        private_id_fun,
                        rewards_matrix,
                        strategy_class,
                        location,
                        reward_score=0,
                        thresholds={'death':0,
                                    'spawn':100,
                                    'instant_death':-np.inf,
                                    'instant_spawn':np.inf},
                        effective_radius=np.inf,
                        stress_penalty_fun=lambda x : 0,
                        bounding_box=np.inf * np.array([-1, 1, -1, 1]),
                        wrap_type=None,
                        food_requirement=10):
        self.ID                 = ID
        self.private_ID         = private_id_fun()
        self.private_id_fun     = private_id_fun # This will be used for private ID requests from spawned copies
        self.rewards_matrix     = rewards_matrix
        self.alive_status       = True
        self.location           = location
        self.strategy           = strategy_class(self.ID, self.private_ID, rewards_matrix)
        self.reward_score       = reward_score
        self.thresholds         = thresholds
        self.effective_radius   = effective_radius
        self.stress_penalty_fun = stress_penalty_fun
        self.food_requirement   = food_requirement

        self.bound_box_method           = move_strategies.apply_bbox(bounding_box)
        self.apply_wrap_method          = move_strategies.apply_wrap(wrap_type, bounding_box)
        self.prepare_wrap_method        = move_strategies.prepare_wrap(wrap_type, bounding_box)


    def get_player_game_state(self):
        # get_player_game_state:
        #     input: none
        #     output: dictionary of several of Player's data members, which will be passed to the play() function:
        #         current_reward_score
        #         thresholds ['death','spawn','instant_death','instant_spawn']
        state = {'current_reward_score' : self.reward_score,
                 'thresholds'           : self.thresholds,
                 'food_requirement'     : self.food_requirement,
                 'location'             : self.get_location()}
        return state

    def get_ID(self):
        return self.private_ID
        # return self.ID


    def get_type_ID(self):
        return self.ID
        # return self.ID


    def get_location(self):
        # get_location:
        #     return location
        return self.location

    def get_effective_radius(self):
        # get_effective_radius:
        #     return effective_radius
        return self.effective_radius

    def distance_to_player(self, other_player):
        other_player_location = other_player.get_location()
        my_location = self.get_location()
        distance = np.linalg.norm(other_player_location - my_location)
        return distance

    def can_see_player(self, other_player):
        # Determines whether another player is visible to this player
        return self.distance_to_player(other_player) <= self.effective_radius

    def is_alive(self):
        # is_alive:
        #     input: none
        #     output: True if alive, False if dead
        return self.alive_status

    def add_reward(self, new_reward):
        self.reward_score += new_reward

    def get_current_reward(self):
        return self.reward_score

    def harvest(self,harvest_reward):
        # harvest:
        #     input: reward
        #     adds reward to current_reward_score
        self.add_reward(harvest_reward)


    def feed(self):
        # feed:
        #     input: none
        #     subtracts food_requirements from current_reward_score
        self.add_reward(-self.food_requirement)

    def stress(self, num_of_visible_neighbors):
        stress_penalty = self.stress_penalty_fun(num_of_visible_neighbors)
        self.add_reward(-stress_penalty)

    def play(self, opponent_ID):
        # play:
        #     inputs: opponent's ID, player_game_state
        #     output: decision (cooperate = 1, betray = 0)
        #     runs play_strategy.play() with inputs, returns the output
        my_game_state = self.get_player_game_state()
        decision = self.strategy.play(opponent_ID, my_game_state)
        return decision

    def update(self, opponent_ID, my_decision, opponent_decision):
        # update:
        #     inputs: opponent's ID, player's decision, opponent's decision, player_game_state
        #         updates current reward - adds the RM's result for decision pair to player's reward score
        #         runs play_strategy.update() with inputs
        #         runs check_thresholds with instant_death / instant_spawn
        #             --> returns either None (no change), 0 (instant death) or a new Player object (instant spawn)
        reward = self.rewards_matrix[my_decision][opponent_decision]
        self.add_reward(reward)

        my_game_state = self.get_player_game_state()
        self.strategy.update(opponent_ID, my_decision, opponent_decision, my_game_state)

        thresholds_check_result = self.check_thresholds_instant()
        return thresholds_check_result

    def check_thresholds_with_values(self, death_th, spawn_th):
        is_death = self.reward_score <= death_th
        is_spawn = self.reward_score >= spawn_th

        if is_death:
            return self.die()

        if is_spawn:
            return self.spawn()

        return None

    def check_thresholds(self):
        th_death = self.thresholds['death']
        th_spawn = self.thresholds['spawn']

        return self.check_thresholds_with_values(death_th=th_death, spawn_th=th_spawn)


    def check_thresholds_instant(self):
        th_instant_death = self.thresholds['instant_death']
        th_instant_spawn = self.thresholds['instant_spawn']

        self.check_thresholds_with_values(death_th = th_instant_death, spawn_th = th_instant_spawn)


    def die(self):
        # die:
        #     alive_status = False
        #     return 0
        self.alive_status = False
        return 0

    def spawn_player(self):
        # spawn_player:
        #     new_player = copy(self)
        new_player = deepcopy(self)
        new_player.private_ID = self.private_id_fun()
        new_player.location += np.random.rand(2)/1000
        return new_player

    def spawn(self):
        # spawn:
        #     rewards_score /= 2
        #     spawned_player = self.spawn_player()
        #     return spawned_player
        #
        self.reward_score /= 2
        return self.spawn_player()


    def move(self, visible_neighbor_locations):
        # move(neighbors):
        #     updates location using strategy.move(neighbors)
        #     returns location#

        # Prepare visible neighbor locations, in case warp_method is "Torus":
        visible_neighbor_locations = self.prepare_wrap_method(visible_neighbor_locations)

        my_game_state = self.get_player_game_state()
        new_location = self.strategy.move(my_game_state, visible_neighbor_locations, self.effective_radius)

        # Apply wrap-around (if active) or bound-box.
        # In practice, only one has effect (wrap around forces points inside the bounding box)
        new_location = self.apply_wrap_method(new_location)
        new_location = self.bound_box_method(new_location)

        self.location = new_location
        return self.location
