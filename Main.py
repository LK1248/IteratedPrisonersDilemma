import numpy as np
from Player import Player
from StrategyEyeForAnEye import StrategyEyeForAnEye
from StrategySaint import StrategySaint
from StrategyJerk import StrategyJerk
from StrategyRandom import StrategyRandom
import move_strategies
from Game import Game

rewards_matrix = [[-1, 5], [-5, 2]]
initial_reward_score = 70
effective_radius = 1
land_harvest_rate = 2
food_requirement = 3
max_plays_per_generation = 3
stress_penalty_fun = lambda x : 2*max(x-max_plays_per_generation, 0) ** 2.2
private_id_fun = move_strategies.get_new_private_ID(1000000)
num_of_generations = 200

bounding_box = np.array([-1, 1, -1, 1]) * 4
wrap_type = None

can_overpopulate_wo_harvest = max_plays_per_generation * rewards_matrix[1][1] > food_requirement
harvest_area = np.pi * effective_radius ** 2
harvest_rate = land_harvest_rate * harvest_area
is_sustainable = max([N * rewards_matrix[1][1] + harvest_rate / N for N in range(1,max_plays_per_generation)]) > food_requirement

print(f"can_overpopulate_wo_harvest - {can_overpopulate_wo_harvest}\nis_sustainable - {is_sustainable}")



# ID_strategy_list = ID: (strategy class, number of starting players for this strategy)
ID_strategy_list = {0: (StrategyEyeForAnEye, 10),
                    1: (StrategySaint, 10),
                    2: (StrategyJerk, 10),
                    3: (StrategyRandom, 10)}

players_list = []
for ID in ID_strategy_list:
    players_list += [Player( ID                 = ID,
                             private_id_fun     = private_id_fun,
                             rewards_matrix     = rewards_matrix,
                             reward_score       = initial_reward_score,
                             strategy_class     = ID_strategy_list[ID][0],
                             location           = np.random.rand(2)*5,
                             effective_radius   = effective_radius,
                             stress_penalty_fun = stress_penalty_fun,
                             bounding_box       = bounding_box,
                             wrap_type          = wrap_type,
                             food_requirement   = food_requirement,
                             )
                     for i in range(0, ID_strategy_list[ID][1]) ]


game = Game(RM                          = rewards_matrix,
            players_list                = players_list,
            land_harvest_rate           = land_harvest_rate,
            max_plays_per_generation    = max_plays_per_generation,
            show_output=False)

for gen in range(num_of_generations):
    gen_status = game.run_one_generation()
    if not gen_status:
        game.handle_output(lambda: print(f"\n\nGAME OVER - everyone died!\n\n"))
        break
