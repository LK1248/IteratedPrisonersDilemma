import numpy as np
import numpy.matlib
import numpy.linalg

def push_model(location, visible_neighbor_locations, max_norm = 1):
    num_of_neighbors = len(visible_neighbor_locations)

    # Don't move if there are no visible neighbors
    if num_of_neighbors == 0:
        return location

    diffs = np.matlib.repmat(location,num_of_neighbors,1) - visible_neighbor_locations
    norms = np.array([[np.linalg.norm(d)+0.000001] for d in diffs])
    pushes = diffs / (np.matlib.repmat(norms,1,2))
    total_push = sum(pushes)
    if np.linalg.norm(total_push) > max_norm:
        total_push = total_push / np.linalg.norm(total_push) * max_norm

    new_location = location + total_push*0.3

    if np.isnan(new_location[0]):
        a=2

    return new_location

def move_towards_all_other_players(location, visible_neighbor_locations, max_norm = 1):
    num_of_neighbors = len(visible_neighbor_locations)

    if num_of_neighbors == 0:
        new_location = location
    else:
        neighbors_cm = sum(visible_neighbor_locations)/num_of_neighbors
        total_push = location - neighbors_cm

        if np.linalg.norm(total_push) > max_norm:
            total_push = total_push / np.linalg.norm(total_push) * max_norm

        new_location = location + 0.1*total_push # Move away from neighbors

    return new_location


def push_and_pull_model(location, visible_neighbor_locations, max_norm = 1):
    num_of_neighbors = len(visible_neighbor_locations)

    # Don't move if there are no visible neighbors
    if num_of_neighbors == 0:
        return location

    diffs = np.matlib.repmat(location,num_of_neighbors,1) - visible_neighbor_locations
    norms = np.array([[np.linalg.norm(d)+0.000001] for d in diffs])
    normalized_diffs = diffs /  (np.matlib.repmat(norms,1,2))
    factors =  1/(np.matlib.repmat(norms,1,2)) - 1.7
    pushes = normalized_diffs * factors
    total_push = sum(pushes)
    if np.linalg.norm(total_push) > max_norm:
        total_push = total_push / np.linalg.norm(total_push) * max_norm

    new_location = location + total_push*0.3

    if np.isnan(new_location[0]):
        a=2

    return new_location
