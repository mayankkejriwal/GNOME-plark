
from simulator.flag_config import flag_config_dict
import numpy as np
from simulator.utility_actions import *


def null_action():
    """
    :return: successful_action code
    """
    print('executing null action...')
    return flag_config_dict['successful_action'] # does nothing; code is always a success


def flip_pelican_counter(pelican_player, current_gameboard, is_meet):
    """
    :return: action code
    """
    print(f'setting MAD to {is_meet} for {pelican_player.player_name}')
    pelican_player.manipulate_MAD(new_MAD=is_meet)
    return flag_config_dict['successful_action']


def update_sonobuoys(current_gameboard, sonobuoy_dict):
    """
    The sonobuoy dict is a dictionary with the sonobuoy name as key and new state as value. We do not do any checks.
    :return: action code
    """
    for k, v in sonobuoy_dict.items():
        print('updating state of sonobuoy ', k,' from ',current_gameboard['weapons_inventory'][k].state,' to ',v)
        current_gameboard['weapons_inventory'][k].state = v

    return flag_config_dict['successful_action']


def move_panther(player, current_gameboard, panther_path):
    """
    :return: action code
    """
    if not panther_path:
        print('there is no path specified. You must specify a path, even if you just stay on the same hex...')
        return flag_config_dict['failure_code']

    if panther_path[0] != player.current_position.location_name:
        print('Your path does not begin where you are...')
        print(panther_path)
        return flag_config_dict['failure_code']

    if len(panther_path) - 1 > current_gameboard['max_panther_path_length']:
        print('Your path is too long...')
        print(panther_path)
        return flag_config_dict['failure_code']

    for i in range(0, len(panther_path)-1): # let's check for path validity
        if panther_path[i+1] not in current_gameboard['location_map'][panther_path[i]].serialize_neighbors():
            print('the path consists of non-adjacent locations...')
            print(panther_path)
            return flag_config_dict['failure_code']

    # everything seems to have succeeded
    player.current_position = current_gameboard['location_map'][panther_path[-1]]
    print('setting position of ',player.player_name,' to ',panther_path[-1],' and appending path history...')
    print(panther_path)
    player.path_history.append(panther_path)
    print('player has been successfully moved...')
    return flag_config_dict['successful_action']


def move_pelican_drop_weapons(player, current_gameboard, pelican_path, weapons_dict):
    """
    pelican_path: a list of location_name(s) that is the 'path' that your pelican will be navigating. We will check for
    correctness, including (i) whether the first element in the list is the pelican's current position, (ii) also that
    the path is valid, (iii) the path is of valid length
     weapons_dict: a dictionary, where the key is a location_name (that must occur on your pelican_path) and the value
     is a set that contains weapon instance-IDs

     Note that the player can be moved without the weapons being dropped successfully. We check for both separately.
     In either case, it's an all or nothing: either all the weapons in weapons_dict get dropped, or none get dropped.
     Either the player is able to move the full path, or stays put. We don't do things halfway.
    :return: action code
    """
    if not pelican_path:
        print('there is no path specified. Best to have selected null action instead...')
        return flag_config_dict['failure_code']

    if pelican_path[0] != player.current_position.location_name:
        print('Your path does not begin where you are...')
        print(pelican_path)
        return flag_config_dict['failure_code']

    if len(pelican_path) > current_gameboard['max_pelican_path_length']:
        print('Your path is too long...')
        print(pelican_path)
        return flag_config_dict['failure_code']

    for i in range(0, len(pelican_path)-1): # let's check for path validity
        if pelican_path[i+1] not in current_gameboard['location_map'][pelican_path[i]].serialize_neighbors():
            print('the path consists of non-adjacent locations...')
            print(pelican_path)
            return flag_config_dict['failure_code']

    # everything seems to have succeeded
    player.current_position = current_gameboard['location_map'][pelican_path[-1]]
    print('setting position of ', player.player_name, ' to ', pelican_path[-1], ' and appending path history...')
    print(pelican_path)
    player.path_history.append(pelican_path)
    print('player has been successfully moved...now dropping weapons, if any.')

    if weapons_dict:
        for location, weapon_names in weapons_dict.items():
            if location not in pelican_path:
                print('weapon is not being dropped on your path...')
                _re_add_weapons_to_bay(player, current_gameboard, weapons_dict)
                print('weapons-deployment did not succeed...')
                return flag_config_dict['failure_code']
            else:
                for name in weapon_names:
                    ww = current_gameboard['weapons_inventory'][name]
                    if ww.weapon_class == 'sonobuoy':
                        _drop_sonobuoy(current_gameboard, name, location)
                    elif ww.weapon_class == 'torpedo':
                        _drop_torpedo(current_gameboard, name, location)

    print('weapons deployment and movement of player succeeded.')
    return flag_config_dict['successful_action']


def _re_add_weapons_to_bay(player,current_gameboard,weapons_dict):
    print('we must re-add weapons to weapons bay of ',player.player_name)
    for v in weapons_dict.values():
        for w in v:
            if current_gameboard['weapons_inventory'][w].weapon_class == 'sonobuoy':
                print('re-adding sonobuoy ',w,' to the weapons bay of ',player.player_name)
                player.weapons_bay['sonobuoy'].add(current_gameboard['weapons_inventory'][w])
            elif current_gameboard['weapons_inventory'][w].weapon_class == 'torpedo':
                print('re-adding torpedo ', w, ' to the weapons bay of ', player.player_name)
                player.weapons_bay['torpedo'].add(current_gameboard['weapons_inventory'][w])
    return


def move_update_torpedoes(current_gameboard):
    """
    :return: action code
    """
    print('in function move_update_torpedoes')
    #step 1: determine plark, its speed and torpedo detection range
    plark = None
    speed = 'stopped'
    for p in current_gameboard['players']:
        if p.player_class == 'Panther':
            plark = p
            if plark.path_history:
                k = len(plark.path_history[-1])-1
                for m, n in current_gameboard['plark_speed'].items():
                    if n == k:
                        speed = m
                        break

            break

    print('plark speed has been determined to be ', speed)
    det_range = current_gameboard['detection_range'][speed]
    print('Hence, detection range is ', str(det_range))


    for weapon_name, weapon in current_gameboard['weapons_inventory'].items():
        if weapon.weapon_class != 'torpedo':
            print(weapon_name,' is not a torpedo. Moving along...')
            continue
        if weapon.state == 'undropped' or weapon.state == 'removed':
            print(weapon_name, ' is a torpedo but has not been dropped, or has been removed. Moving along...')
            continue

        if weapon.location.triggers_torpedo_sensor(weapon, current_gameboard):
            print('torpedo sensor has been triggered in location ',weapon.location.location_name)
            print('setting target location of ',weapon_name,' to this location.')
            target_location = weapon.location
        else: # this is the complex part of this function. may require debugging...

            closest_dis = weapon.location.locate_nearest_disturbed_water(current_gameboard)

            if closest_dis and closest_dis.calculate_distance(current_gameboard,weapon.location) > current_gameboard['torpedo_listening_range']:
                print('closest_dis is too far from torpedo_listening_range. Setting it to None...')
                closest_dis = None


            torpedo_dis, torpedos = weapon.location.locate_dropped_torpedos_within_range(current_gameboard, current_gameboard['torpedo_detection_range'])
            if torpedo_dis:
                torpedo_locs = set([i.location for i in torpedos])
            else:
                torpedo_locs = set()
            print('lets determine the torpedo\'s target...')
            target_location = _pick_torpedo_target(current_gameboard, weapon, plark.current_position, det_range, closest_dis, torpedo_dis, torpedo_locs)


            if target_location is None:
                print('no target location for torpedo was returned. Guess it stays put...')
                target_location = weapon.location
            elif target_location != weapon.location:
                print('target location for torpedo was returned as location ',target_location.location_name)
                print('computing shortest path...')
                shortest_path = weapon.location.compute_shortest_path(current_gameboard, target_location)[1:] # let's not count the current position

                target_location = current_gameboard['location_map'][shortest_path[-1]]
                if len(shortest_path) > current_gameboard['torpedo_speed'][weapon.state]: # has to be either first_turn or second_turn
                    print('shortest path is too long for torpedo to move the full distance. Setting new target location along shortest path...')
                    target_location = current_gameboard['location_map'][shortest_path[0:current_gameboard['torpedo_speed'][weapon.state]][-1]]
                    print('target location is ',target_location.location_name)

        print(weapon_name, ' location has been updated from ', weapon.location.location_name, ' to ',
              target_location.location_name)
        weapon.location = target_location # if the torpedo sensor was triggered, this does not cause any change, otherwise the torpedo will move to the new location


        if plark.current_position == target_location: # this is the only thing that leads to something happening
            print('the plark is right where ',weapon_name, ' is!')
            for w_name, w in current_gameboard['weapons_inventory'].items():
                if w.weapon_class != 'torpedo':
                    continue
                if w.state == 'undropped' or w.state == 'removed':
                    continue
                print('rolling dice for torpedo ',w_name)
                die_result = _roll_die()
                print('panther rolled dice. value came up ',str(die_result))
                if w_name != weapon_name:
                    print('dice was not rolled for the torpedo that hit the plark. Moving on...')
                    continue

                print('if we got here, then ',w_name,' must equal ',weapon_name)
                if die_result == 1 or die_result == 2:
                    print('Die result came up 1 or 2. changing plark damage status from ',plark.damage_status,' to sunk.')
                    plark.damage_status = 'sunk'
                elif die_result == 3 or die_result == 4:
                    if plark.damage_status == 'damaged':
                        print('Die result came up 3 or 4. changing plark damage status from ', plark.damage_status, ' to sunk.')
                        plark.damage_status = 'sunk'
                    else:
                        print('Die result came up 3 or 4. changing plark damage status from ', plark.damage_status, ' to damaged.')
                        plark.damage_status = 'damaged'

                if die_result == 5 or die_result == 6:
                    print(f'Torpedo {weapon_name} miss panther at location {plark.current_position.location_name}')
                else:
                    print(f'Update explosion status of location {plark.current_position.location_name} from False to '
                          f'True because torpedo {weapon_name} hit panther')
                    plark.current_position.underwater_explosion = True

                print('changing state of ',weapon_name,' from ',weapon.state,' to removed and setting location from ',weapon.location.location_name,' to None.')
                weapon.state = 'removed'
                weapon.location = None

        else:
            print('flipping torpedo ',weapon_name)
            flip_torpedo(weapon)

    return flag_config_dict['successful_action']


def _pick_torpedo_target(current_gameboard, weapon, plark_pos, plark_det_range, closest_dis, torpedo_dis, torpedo_locs):
    """

    :param current_gameboard:
    :param weapon:
    :param plark_pos: location of the plark
    :param closest_dis: either None or location of the closest disturbed water if in listening range
    :param torpedo_dis: either None or shortest path distance to closest active torpedo(s)
    :param torpedo_locs: set of locations with torpedos in them
    :return:
    """
    print('in function _pick_torpedo_target')
    candidate_locations = set()

    if torpedo_dis and torpedo_dis <= weapon.location.calculate_distance(current_gameboard, plark_pos): # do torpedo locs belong in candidate set?
        if not closest_dis:
            print('adding torpedo_locs to candidate_locations')
            candidate_locations = candidate_locations.union(torpedo_locs)
        elif torpedo_dis <= weapon.location.calculate_distance(current_gameboard, closest_dis):
            print('adding torpedo_locs to candidate_locations')
            candidate_locations = candidate_locations.union(torpedo_locs)

    if weapon.location.calculate_distance(current_gameboard, plark_pos) <= plark_det_range: # does plark_pos belong in candidate set?
        if not torpedo_dis:
            if not closest_dis:
                print('adding plark_pos to candidate_locations')
                candidate_locations.add(plark_pos)
            elif weapon.location.calculate_distance(current_gameboard, plark_pos) <= weapon.location.calculate_distance(current_gameboard, closest_dis):
                print('adding plark_pos to candidate_locations')
                candidate_locations.add(plark_pos)
        elif weapon.location.calculate_distance(current_gameboard, plark_pos) <= torpedo_dis:
            if not closest_dis:
                print('adding plark_pos to candidate_locations')
                candidate_locations.add(plark_pos)
            elif weapon.location.calculate_distance(current_gameboard, plark_pos) <= weapon.location.calculate_distance(current_gameboard, closest_dis):
                print('adding plark_pos to candidate_locations')
                candidate_locations.add(plark_pos)

    if closest_dis: # does closest_dis belong in candidate set?
        if not torpedo_dis:
            if weapon.location.calculate_distance(current_gameboard, closest_dis) <= weapon.location.calculate_distance(current_gameboard, plark_pos):
                print('adding closest_dis to candidate_locations')
                candidate_locations.add(closest_dis)
        elif weapon.location.calculate_distance(current_gameboard, closest_dis) <= torpedo_dis \
            and weapon.location.calculate_distance(current_gameboard, closest_dis) <= weapon.location.calculate_distance(current_gameboard, plark_pos):
            print('adding closest_dis to candidate_locations')
            candidate_locations.add(closest_dis)


    if not candidate_locations:
            print('candidate_locations are empty. Returning None...')
            return None

    else:
        samples = list(candidate_locations)
        np.random.shuffle(samples)
        for sample in samples:

            if weapon.location.calculate_distance(current_gameboard, sample) > current_gameboard['torpedo_listening_range']: # this can happen

                print('we picked candidate location ', sample.location_name,' but it is not within the torpedo_listening_range. Getting next sample...')
                continue
            else:
                print('we have picked candidate location...',sample.location_name)
                return sample

        print('no candidate location is within torpedo_listening_range or otherwise eligible. Returning None...')
        return None


def _roll_die():
    """
    :return: action code
    """
    print('rolling dice...')
    return np.random.choice([1,2,3,4,5,6])



def _drop_sonobuoy(current_gameboard, sonobuoy_name, location_name):
    print('dropping sonobuoy ',sonobuoy_name,' on location ',location_name)
    current_gameboard['weapons_inventory'][sonobuoy_name].location=current_gameboard['location_map'][location_name]
    current_gameboard['weapons_inventory'][sonobuoy_name].state = 'cold'
    print('sonobuoy successfully dropped and state set to cold.')


def _drop_torpedo(current_gameboard, torpedo_name, location_name):
    print('dropping torpedo ', torpedo_name, ' on location ', location_name)
    current_gameboard['weapons_inventory'][torpedo_name].location = current_gameboard['location_map'][location_name]
    current_gameboard['weapons_inventory'][torpedo_name].state = 'first_turn'
    print('torpedo successfully dropped and state set to first_turn.')


def update_water_counters(current_gameboard):
    """

    :return:
    """
    for location_name, location in current_gameboard['location_map'].items():
        if location.disturbed_water:
            print('setting disturbed water status of location ',location.location_name,' to False...')
            location.disturbed_water = False
        elif location.underwater_explosion:
            print('setting disturbed water status of location ', location.location_name, ' to True, and underwater_explosion status to False...')
            location.underwater_explosion = False
            location.disturbed_water = True

    return flag_config_dict['successful_action']

