import numpy as np
from simulator.flag_config import flag_config_dict


"""
Purposes of these file is to contain functions which might be used for injecting novelty. Novelties could cause some 
rules of actions change for Panther/Pelican, or adding new attributes to objects like weapons, player, and etc.
"""


def torpedo_attack_again_if_miss(current_gameboard, weapon_name, weapon, die_result):
    """
    Torpedo could re-attach plark if missing target on the first turn. Otherwise, work as before
    :param current_gameboard:
    :param weapon_name: current torpedo name
    :param weapon: torpedo object which need to change state
    :param die_result: int number of die between 1 and 6
    :return:
    """
    if weapon.state == 'first_turn' and (die_result == 5 or die_result == 6):
        print(f'Torpedo {weapon_name} misses the target and die result is {die_result}, state change to second turn')
        weapon.state = 'second_turn'
    else:
        print(f'Changing state of {weapon_name} from {weapon.state} to removed and setting location from {weapon.location.location_name} to None.')
        weapon.state = 'removed'
        weapon.location = None


def drop_sonobuoy_in_two_layer(current_gameboard, sonobuoy_name, location_name):
    """
    When sonobuoy dropped, randomly decide its depth to be Shallow or Deep. This property might affect detection
    range of sonobuoy and torpedo if panther and weapons result in different layers
    :param current_gameboard:
    :param sonobuoy_name: string name of sonobuoy name
    :param location_name: string name of location name
    :return:
    """
    print(f'Dropping sonobuoy {sonobuoy_name} on location {location_name}')
    current_gameboard['weapons_inventory'][sonobuoy_name].location=current_gameboard['location_map'][location_name]
    current_gameboard['weapons_inventory'][sonobuoy_name].state = 'cold'
    print('Sonobuoy successfully dropped and state set to cold.')

    # Setting layer, key of this property is "two_layer"
    cur_attribute = None
    cur_weapon = None
    for name, weapon in current_gameboard['weapons_inventory'].items():
        if name == sonobuoy_name:
            cur_weapon = weapon
            for att_name, attribute in weapon.attributes.items():
                if att_name == 'two_layer':
                    cur_attribute = attribute
                    break
            break

    # One key and one value of list usually
    for k, v in cur_attribute.items():
        candidate_list = v
    cur_weapon.attributes['two_layer'] = {
        np.random.choice(candidate_list): candidate_list
    }
    print(f'Setting sonobuoy {sonobuoy_name} with depth {cur_weapon.attributes["two_layer"].keys()}')


def panther_decision_in_two_layer(player, current_gameboard, panther_path):
    """
    Panther also decide its depth to either Shallow or Deep
    :param player: current player, it should be panther mostly
    :param current_gameboard: dict of gameboard
    :param panther_path: list of string of path decide by panther strategy
    :return: flag code to indicate failure or success
    """
    player.current_position = current_gameboard['location_map'][panther_path[-1]]
    print('setting position of ',player.player_name,' to ',panther_path[-1],' and appending path history...')
    print(panther_path)
    player.path_history.append(panther_path)
    print('player has been successfully moved...')

    # key is "two_layer"
    candidate_list = list(player.additional_attributes['two_layer'].values())[0]
    random_depth = np.random.choice(candidate_list)
    player.additional_attributes['two_layer'] = {
        random_depth: candidate_list
    }
    player.additional_attributes_history.append(random_depth)  # add to history
    print(f'{player.player_name} decides its depth to be {random_depth}')


def sonobuoy_consider_two_layer(current_gameboard, s_updates, sonobuoy_panther_found, weapon, plark_location, player, det_range):
    """
    Since depth is either Shallow or Deep, sonobuoy now could detect plark with considering depth
    If at different depth, detection range would be reduce by 2
    Otherwise, it would be same as before
    :param current_gameboard: dict of current game board
    :param s_updates: sonobuoy which needs to be updated to either hot or cold
    :param sonobuoy_panther_found: record of locations of sonobuoy that plark knows
    :param weapon: current weapon object
    :param plark_location: location object of panther
    :param player: panther player
    :param det_range: current detection range for panther which determined by previous speed
    :return:
    """
    weapon_name = weapon.weapon_name
    cur_weapon_location = weapon.location
    plark2weapon_dist = plark_location.calculate_distance(current_gameboard, cur_weapon_location)
    depth_hist = player.additional_attributes_history

    if len(depth_hist) >= 2 and depth_hist[-1] != depth_hist[-2]:  # plark changes its depth currently
        print(f'{player.player_name} says POPCORN to pelican')
        if 'panther' not in current_gameboard['chat_log']:
            current_gameboard['chat_log']['panther'] = set()
        current_gameboard['chat_log']['panther'].add('POPCORN')

        weapon_depth = list(weapon.attributes['two_layer'].keys())[0]
        plark_depth = list(player.additional_attributes['two_layer'].keys())[0]
        if weapon_depth != plark_depth and plark2weapon_dist <= det_range - 2:
            print(f'sonobuoy {weapon_name} is within plark det_range. updating to hot...')
            s_updates[weapon_name] = 'hot'
            sonobuoy_panther_found.add(cur_weapon_location)

        elif weapon_depth == plark_depth:
            print(f'{player.player_name} and sonobuoy {weapon_name} both at {weapon_depth}, updating to hot...')
            print(f'sonobuoy {weapon_name} is within plark det_range. updating to hot...')
            s_updates[weapon_name] = 'hot'
            sonobuoy_panther_found.add(cur_weapon_location)
        else:
            print(f'{player.player_name} at depth {plark_depth}, but weapon {weapon_name} at depth '
                  f'{weapon_depth}, and they are not within range {det_range - 2}, do not set to hot...')
    else:
        print(f'sonobuoy {weapon_name} is within plark det_range. updating to hot...')
        s_updates[weapon_name] = 'hot'
        sonobuoy_panther_found.add(cur_weapon_location)


def torpedo_detect_plark_with_layer(current_gameboard, weapon, plark_pos, plark_det_range, torpedo_dis, closest_dis, candidate_locations, player):
    """
    torpedo could work correctly under two layers condition
    If POPCORN claimed before, it should reduce it detection range if at different layers
    :param current_gameboard: dict of current game board
    :param weapon: weapon object which currently want to find a target
    :param plark_pos: current plark location object
    :param plark_det_range: plark detection range
    :param torpedo_dis: int number of current nearest distance from current weapon to other torpedos
    :param closest_dis: closest explosion/disturbed water locatison object
    :param candidate_locations: candidate locations which target might pick to attack
    :param player: panther player object
    :return:
    """
    plark2weapon_dist = weapon.location.calculate_distance(current_gameboard, plark_pos)

    if len(current_gameboard['chat_log']) > 0 and 'POPCORN' in current_gameboard['chat_log']['panther']:
        print(f'panther claims POPCORN previously, torpedo {weapon.weapon_name} should reduce its detection range'
              f'if at different depth')
        weapon_depth = list(weapon.attributes['two_layer'].keys())[0]
        plark_depth = list(player.additional_attributes['two_layer'].keys())[0]

        if weapon_depth != plark_depth and plark2weapon_dist > plark_det_range - 2:
            print(f'panther and torpedo {weapon.weapon_name} at different layer and plark is too far from {weapon.weapon_name}')
            pass
        elif weapon_depth == plark_depth and plark2weapon_dist > plark_det_range:
            print(f'panther and torpedo {weapon.weapon_name} at same layer, but plark is too far from {weapon.weapon_name}')
            pass
        else:
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

    elif plark2weapon_dist <= plark_det_range:
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


