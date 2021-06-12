from simulator.action_choices import *
from simulator.auxiliary_functions import _convert_ijk_to_string
import numpy as np
import networkx as nx


"""
If you're a pelican, you only need to implement the first function until further notice.
Leave the other functions as is, or copy them over to your new agent.

If you're a panther, you should implement only the panther phase until further notice.

Pelican Agent v1
- Moving Strategy: 
    1. Do not go to the location where have been visited in current turn
    2. For the first 10 turns search areas of GHJ since plark start in these area
    3. For the rest of turns, do the random walk
- Weapon Strategy:
    1. If sonobuoy is hot, go to the location and drop torpedo
    2. If pelican's MAD is turn on, go to the location and drop torpedo, or search previous path where plark has a high
    probabilities existing.
"""

def make_pelican_phase_move(player, current_gameboard, allowable_actions, code):
    """
    Current strategy is to chart a 'random' walk path of length
    :param player:
    :param current_gameboard:
    :param allowable_actions:
    :param code:
    :return:
    """
    if player.player_class != 'Pelican':
        print('Non-Pelican is trying to make pelican phase move...')
        raise Exception

    if move_pelican_drop_weapons not in allowable_actions:
        print('move_pelican_drop_weapons not in allowable_actions for ',player.player_name,'. Returning null action')
        return null_action, dict()

    path = list()
    path.append(player.current_position.location_name)
    weapons_dict = dict()
    G = current_gameboard['game_graph']

    # Drop torpedo if the sonobuoy is hot
    for weapon_name, weapon in current_gameboard['weapons_inventory'].items():
        if weapon.weapon_class == 'sonobuoy' and weapon.state == 'hot':
            print(f'pelican currently find hot sonobuoy {weapon_name} at locatin {weapon.location.location_name}')
            shortest_path = nx.shortest_path(G, source=player.current_position.location_name, target=weapon.location.location_name)
            path += shortest_path[1:]
            if path[-1] not in weapons_dict:
                weapons_dict[path[-1]] = set()
            if player.weapons_bay['torpedo']:
                weapons_dict[path[-1]].add(player.eject_torpedo().weapon_name)
                print(f'We will drop torpedo {weapons_dict[path[-1]]} on location {path[-1]}')
            break  # currently drop only one torpedo in each turn

    # Drop torpedo if pelican's MAD is turn on
    # Or search previous path pelican has gone through although it don't know which location exactly

    if current_gameboard['num_turns'] < 5:
        print('Current turn < 5')
        focusing_region = ['G', 'H', 'J']
        nodes = [_convert_ijk_to_string(row, col, '') for row in range(1, 11) for col in range(1, 11)]
        if any([1 if region in player.current_position.location_name else 0 for region in focusing_region]):
            print('Random walk to find plark')
            _random_walk(current_gameboard, path, player, weapons_dict)

        else:
            candidate_location = np.random.choice(nodes) + np.random.choice(focusing_region)
            print(f'find shortest path to {candidate_location}')

            shortest_path = nx.shortest_path(G, source=player.current_position.location_name, target=candidate_location)
            path += shortest_path[1:current_gameboard["max_pelican_path_length"] - len(path)]
    elif current_gameboard['num_turns'] < 15:
        print('Current turn < 15')
        focusing_region = ['A', 'B', 'C']
        # nodes = [_convert_ijk_to_string(row, col, '') for row in range(1, 11) for col in range(1, 11)]
        nodes = ['0503', '0508']
        candidate_location = np.random.choice(nodes) + np.random.choice(focusing_region)
        print(f'find shortest path to {candidate_location}')

        shortest_path = nx.shortest_path(G, source=player.current_position.location_name, target=candidate_location)
        path += shortest_path[1:current_gameboard["max_pelican_path_length"] - len(path)]

        if path[-1] == candidate_location and player.weapons_bay['sonobuoy']:
            if path[-1] not in weapons_dict:
                weapons_dict[path[-1]] = set()
            if not is_sonobuoy_in_current_location(current_gameboard, path[-1]):
                weapons_dict[path[-1]].add(player.eject_sonobuoy().weapon_name)
                print(f'we will drop sonobuoy {weapons_dict[path[-1]]} on location {path[-1]}')
            else:
                print(f'There is already one sonubuoy in the current location {path[-1]}, do not drop more...')

    else:
        # Do the random walk
        _random_walk(current_gameboard, path, player, weapons_dict)

    params = dict()
    params['player'] = player
    params['current_gameboard'] = current_gameboard
    params['pelican_path'] = path
    params['weapons_dict'] = weapons_dict

    return move_pelican_drop_weapons, params


def make_madman_phase_move(player, current_gameboard, allowable_actions, code):
    if player.player_class != 'Panther':
        print('Non-Panther is trying to make madman phase move...')
        raise Exception


def make_maypole_phase_move(player, current_gameboard, allowable_actions, code):
    if player.player_class != 'Panther':
        print('Non-Panther is trying to make maypole phase move...')
        raise Exception


def make_panther_phase_move(player, current_gameboard, allowable_actions, code):
    if player.player_class != 'Panther':
        print('Non-Panther is trying to make panther phase move...')
        raise Exception


def make_bloodhound_phase_move(player, current_gameboard, allowable_actions, code):
    if player.player_class != 'Panther':
        print('Non-Panther is trying to make bloodhound phase move...')
        raise Exception


def initialization_routine(agent, current_gameboard):
    if agent.agent_type == 'Panther':
        agent.init_position = '0503H'
    elif agent.agent_type == 'Pelican':
        agent.init_position = '0302A'
        agent.init_weapons_bay = dict()
        agent.init_weapons_bay['sonobuoy_count'] = 12
        agent.init_weapons_bay['torpedo_count'] = 36

    else:
        print('agent has unrecognized type. Cannot initialize position')
        raise Exception


def _random_walk(current_gameboard, path, player, weapons_dict):

    while len(path) < current_gameboard['max_pelican_path_length']:
        m = [i for i in current_gameboard['location_map'][path[-1]].neighbors if i.location_name != 'escape'] # pelican can't leave the board
        np.random.shuffle(m)
        for i in range(len(m)):
            if m[i].location_name not in path:
                next_move = m[i]
                break

        print(f'Appending location {next_move.location_name} to return-path of {player.player_name}')
        path.append(next_move.location_name)

        if path[-1] not in weapons_dict:
            weapons_dict[path[-1]] = set()

        # Drop sonobuoy randomly
        if np.random.uniform(0, 1) < 0.05 and player.weapons_bay['sonobuoy']:
            weapons_dict[path[-1]].add(player.eject_sonobuoy().weapon_name)
            print(f'we will drop sonobuoy {weapons_dict[path[-1]]} on location {path[-1]}')
        # Drop sonobuoy evenly at each region
        # drop_sonobuoy_evenly(current_gameboard, path, player, weapons_dict)


def drop_sonobuoy_evenly(current_gameboard, path, player, weapons_dict):
    visited_regions = set()
    for weapon_name, weapon in current_gameboard['weapons_inventory'].items():
        if weapon.weapon_class == 'sonobuoy' and (weapon.state != 'undropped' or weapon.state != 'removed'):
            l_name = weapon.location.location_name
            visited_regions.add(l_name[-1])
    if np.random.uniform(0, 1) < 0.05 and player.weapons_bay['sonobuoy'] and path[-1][-1] not in visited_regions:
        weapons_dict[path[-1]].add(player.eject_sonobuoy().weapon_name)
        print(f'we will drop sonobuoy {weapons_dict[path[-1]]} on location {path[-1]}')


def is_sonobuoy_in_current_location(current_gameboard, cur_location):
    for name, weapon in current_gameboard['weapons_inventory'].items():
        if weapon.weapon_class == 'sonobuoy' and weapon.location and weapon.location.location_name == cur_location:
            return True
    return False


def _build_decision_agent_methods_dict():
    """

    This function builds the decision agent methods dictionary.
    :return: The decision agent dict. Keys should be exactly as stated in this example, but the functions can be anything
    as long as you use/expect the exact function signatures we have indicated in this document.
    """
    ans = dict()
    ans['make_pelican_phase_move'] = make_pelican_phase_move
    ans['make_madman_phase_move'] = make_madman_phase_move
    ans['make_maypole_phase_move'] = make_maypole_phase_move
    ans['make_panther_phase_move'] = make_panther_phase_move
    ans['make_bloodhound_phase_move'] = make_bloodhound_phase_move
    ans['initialization_routine'] = initialization_routine
    ans['agent_type'] = 'Pelican'
    return ans


decision_agent_methods = _build_decision_agent_methods_dict() # this is the main data structure that is needed by gameplay
