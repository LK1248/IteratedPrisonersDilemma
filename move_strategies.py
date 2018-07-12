import numpy as np
import numpy.matlib as mb
import numpy.linalg
import random


# def get_new_private_ID():
#     get_new_private_ID.currID += 1
#     return get_new_private_ID.currID
#
# get_new_private_ID.currID = 1000000


def get_new_private_ID(start_ID):

    def inner():
        inner.curr_ID += 1
        return inner.curr_ID

    inner.curr_ID = start_ID
    return inner



# Define the following decorators in Game. They will be passed to Player during init (and used in player.strategy)
def prepare_wrap(wrap_type = None, bbox = np.inf * np.array([-1, 1, -1, 1])): # Can be None or 'Torus'
    def inner(locations):
        if wrap_type is None:
            pass
        elif wrap_type == 'Torus':
            if any(np.isinf(bbox)):
                # raise ValueError("Bounding box must be defined for wrap-around to work")
                pass
            else:
                num_of_locations = len(locations)
                dx = bbox[1] - bbox[0]
                dy = bbox[3] - bbox[2]
                ddx = mb.repmat(np.array([dx, 0]), num_of_locations, 1)
                ddy = mb.repmat(np.array([0, dy]), num_of_locations, 1)

                locations11 = locations - ddx - ddy
                locations12 = locations       - ddy
                locations13 = locations + ddx - ddy
                locations21 = locations - ddx
                locations22 = locations
                locations23 = locations + ddx
                locations31 = locations - ddx + ddy
                locations32 = locations       + ddy
                locations33 = locations + ddx + ddy

                locations = np.concatenate((locations11, locations12, locations13,
                                            locations21, locations22, locations23,
                                            locations31, locations32, locations33 ), axis=0)


        return locations
    return inner


def apply_wrap(wrap_type = None, bbox = np.inf * np.array([-1, 1, -1, 1])): # Can be None or 'Torus'
    def inner(location):
        if wrap_type is None:
            pass
        elif wrap_type == 'Torus':
            dx = bbox[1] - bbox[0]
            dy = bbox[3] - bbox[2]

            if location[0] < bbox[0]: location[0] += dx
            if location[0] > bbox[1]: location[0] -= dx
            if location[0] < bbox[2]: location[1] += dy
            if location[0] > bbox[3]: location[1] -= dy

        return location
    return inner


def apply_bbox(bbox = np.inf * np.array([-1, 1, -1, 1])):
    def inner(location):

        r = random.randint(0,10)/10
        location[0] = min(max(location[0], bbox[0]+r), bbox[1]-r)
        location[1] = min(max(location[1], bbox[2]+r), bbox[3]-r)

        return location
    return inner


        # Modes:
        #   bounding_box: limits all movement to inside the box [x_min x_max y_min y_max]
        #           defaults to: [-np.inf, np.inf, -np.inf, np.inf]
        #
        #   wrap_around:
        #     requires bounding_box to be defined
        #       If wrap_around == 'Torus':
        #       1. Before move: all neighbors are repeated in a 3x3 matrix around center box
        #       2. After move: all positions are taken modulo the bounding_box dimensions
        #       If wrap_around == 'None':
        #       1. Before move: no change
        #       2. After move: all positions are clipped inside the bounding_box dimensions





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

    return new_location
