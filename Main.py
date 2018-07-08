import numpy as np
from Player import Player
from StrategyEyeForAnEye import StrategyEyeForAnEye
from StrategySaint import StrategySaint
from StrategyJerk import StrategyJerk
from StrategyRandom import StrategyRandom

from Game import Game

rewards_matrix = [[0, 1], [-1, 1]]
effective_radius = 0.8
land_harvest_rate = 10

num_of_generations = 50


# ID_strategy_list = ID: (strategy class, number of starting players for this strategy)
ID_strategy_list = {0: (StrategyEyeForAnEye, 10),
                    1: (StrategySaint, 10),
                    2: (StrategyJerk, 10),
                    3: (StrategyRandom, 10)}

players_list = []
for ID in ID_strategy_list:
    players_list += [Player( ID                 = ID,
                             rewards_matrix     = rewards_matrix,
                             strategy_class     = ID_strategy_list[ID][0],
                             location           = np.random.rand(2),
                             effective_radius   = effective_radius)
                     for i in range(0, ID_strategy_list[ID][1]) ]


game = Game(RM                          = rewards_matrix,
            players_list                = players_list,
            land_harvest_rate           = land_harvest_rate,
            max_plays_per_generation    = np.inf,
            show_output=True)

for gen in range(num_of_generations):
    gen_status = game.run_one_generation()
    if not gen_status:
        game.handle_output(lambda: print(f"\n\nGAME OVER - everyone died!\n\n"))
        break
