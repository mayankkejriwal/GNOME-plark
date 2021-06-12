from simulator.action_choices import *
# from simulator.action_choices import _sonobuoys_search_locations_nearby
import numpy as np
import networkx as nx

"""
If you're a pelican, you only need to implement the first function until further notice.
Leave the other functions as is, or copy them over to your new agent.

If you're a panther, you should implement only the panther phase until further notice.

Panther Agent v1
Two ways to win: (i) escape from the top edges (ii) hide and undamaged
- Moving Strategy:
    1. Check if plark could escape at the beginning and end of the game
    2. For the first 10 turns, we pick top edges which could escape randomly and move upward with the fatest speed
    3. If there were any sonobuoys plark had found previously and currently close to the sonobuoy, move away
    4. Record the sonobuoys plark turn from cold to hot in the Maypole phase
    5. If turns number > 10 and at region ABC, move with speed 1 or 2 toward top edges
    6. If turns number > 10 and at region DEF, move with speed 0 or 1 for hidding
"""

def make_pelican_phase_move(player, current_gameboard, allowable_actions, code):

    if player.player_class != 'Pelican':
        print('Non-Pelican is trying to make pelican phase move...')
        raise Exception


def make_madman_phase_move(player, current_gameboard, allowable_actions, code):
    if player.player_class != 'Panther':
        print('Non-Panther is trying to make madman phase move...')
        raise Exception

    previous_player = current_gameboard['player_turn_sequence'][-1]

    if previous_player.player_class != 'Pelican':
        print('previous player was not pelican-type...')
        if null_action in allowable_actions:
            print('returning null_action')
            return null_action, dict()

    else:
        if current_gameboard['history']['function'][-1] == null_action:
            return null_action, dict()
        last_path = set(previous_player.path_history[-1])
        if player.current_position.location_name in last_path and flip_pelican_counter in allowable_actions:
            print('flipping pelican counter since it passed over plark\'s current position...')
            params = dict()
            params['current_gameboard'] = current_gameboard
            params['pelican_player'] = previous_player
            params['is_meet'] = True
            return flip_pelican_counter, params
        elif previous_player.MAD:
            print('flipping pelican MAD counter back to false')
            params = dict()
            params['current_gameboard'] = current_gameboard
            params['pelican_player'] = previous_player
            params['is_meet'] = False
            return flip_pelican_counter, params

    if null_action in allowable_actions:
        print('returning null_action')
        return null_action, dict()
    else:
        print('something has gone wrong, we should not be here')
        raise Exception



def make_maypole_phase_move(player, current_gameboard, allowable_actions, code):
    if player.player_class != 'Panther':
        print('Non-Panther is trying to make maypole phase move...')
        raise Exception

    speed = 'stopped'
    if player.path_history:
        k = len(player.path_history[-1])-1
        for m, n in current_gameboard['plark_speed'].items():
            if n == k:
                speed = m
                break

    print(f'plark speed has been determined to be {speed}')
    det_range = current_gameboard['detection_range'][speed]
    print(f'Hence, detection range is {det_range}')
    plark_location = player.current_position

    # s_updates = dict()
    # sonobuoy_panther_found = set() if 'sonobuoy_panther_found' not in current_gameboard else current_gameboard['sonobuoy_panther_found']

    # s_updates is weapon we need to change status
    # sonobuoy_panther_found is the sonobuoys that panther has found so far
    s_updates, sonobuoy_panther_found = sonobuoys_search_locations_nearby(current_gameboard, player, plark_location, det_range)

    # for weapon_name, weapon in current_gameboard['weapons_inventory'].items():
    #     if weapon.location is None or weapon.weapon_class == 'torpedo':
    #         continue
    #     else:
    #         cur_weapon_location = weapon.location
    #         print(f'we need to determine new status for sonobuoy {weapon_name} which is currently at {cur_weapon_location.location_name}')
    #         if plark_location.calculate_distance(current_gameboard, cur_weapon_location) <= det_range:
    #             print('sonobuoy is within plark det_range. updating to hot...')
    #             s_updates[weapon_name] = 'hot'
    #             sonobuoy_panther_found.add(cur_weapon_location)
    #             continue
    #         else:
    #             dis = cur_weapon_location.locate_nearest_disturbed_water(current_gameboard)
    #             if dis and dis.calculate_distance(current_gameboard, cur_weapon_location) <= current_gameboard['sonobuoy_disturbed_water_threshold']:
    #                 print('sonobuoy is within sonobuoy_disturbed_water_threshold of disturbed water. updating to hot...')
    #                 s_updates[weapon_name] = 'hot'
    #                 continue
    #
    #             expl = cur_weapon_location.locate_nearest_underwater_explosion(current_gameboard)
    #             if expl and expl.calculate_distance(current_gameboard, cur_weapon_location) <= current_gameboard['sonobuoy_underwater_explosion_threshold']:
    #                 print('sonobuoy is within sonobuoy_underwater_explosion_threshold of disturbed water. updating to hot...')
    #                 s_updates[weapon_name] = 'hot'
    #                 continue
    #
    #             print('sonobuoy stays cold, or is flipped from hot to cold...')
    #             s_updates[weapon_name] = 'cold'

    # Update sonobuoys panther has found so far
    current_gameboard['sonobuoy_panther_found'] = sonobuoy_panther_found

    if s_updates and update_sonobuoys in allowable_actions:
        print('updating sonobuoys')
        params = dict()
        params['current_gameboard'] = current_gameboard
        params['sonobuoy_dict'] = s_updates
        return update_sonobuoys, params

    if null_action in allowable_actions:
        print('returning null_action')
        return null_action, dict()
    else:
        print('something has gone wrong, we should not be here')
        raise Exception



def make_panther_phase_move(player, current_gameboard, allowable_actions, code): # we'll do a random walk
    if player.player_class != 'Panther':
        print('Non-Panther is trying to make panther phase move...')
        raise Exception

    if move_panther not in allowable_actions:
        print('move_panther not in allowable actions. returning null_action...')
        return null_action, dict()

    # recording path of panther move this turn
    path = list()
    path.append(player.current_position.location_name)

    # player, current_gameboard, pelican_path, weapons_dict
    params = dict()
    params['player'] = player
    params['current_gameboard'] = current_gameboard

    G = current_gameboard['game_graph']
    top_edges_escape = [number + region
                        for number in ['0101', '0301', '0501', '0701', '0901']
                        for region in ['A', 'B', 'C']]

    # check if we could escape, this only happen if we are already on one of top locations
    # and there were no more movement in previous turn for panther to move
    could_escape, escape_loc = _check_escape_condition(current_gameboard, path)
    if could_escape:
        print(f'Plark has chance to escape from location {path[-1]}')
        path.append(escape_loc.location_name)
        params['panther_path'] = path
        return move_panther, params  # time to escape.

    # panther record locations of sonobuoys it has accidentally turn on
    # if currently close to those location, panther should move away for avoiding be attached by torpedos
    if current_gameboard['sonobuoy_panther_found']:
        print(f'Panther knew sonobuoys at locations {",".join([i.location_name for i in current_gameboard["sonobuoy_panther_found"]])}')
        for sonobuoy_loc in current_gameboard['sonobuoy_panther_found']:
            if len(path) - 1 >= current_gameboard['max_panther_path_length']:
                break  # break if already move upto max # of movement
            if player.current_position.calculate_distance(current_gameboard, sonobuoy_loc) <= current_gameboard['torpedo_speed']['first_turn']:
                print(f'Panther currently at {player.current_position.location_name} close to {sonobuoy_loc.location_name}, let\'s move away...')
                longest_distance = 0
                candidate_location = None
                for neighbor in player.current_position.neighbors:
                    cur_distance = sonobuoy_loc.calculate_distance(current_gameboard, neighbor)
                    if cur_distance > longest_distance:
                        longest_distance = cur_distance
                        candidate_location = neighbor.location_name
                path.append(candidate_location)
                print(f'Panther currently at {player.current_position.location_name} move to {path[-1]} to away from sonobuoy at {sonobuoy_loc.location_name}')
                break  # currently just try to move away from one of sonobuoys

    # Use fastest speed toward top edges for escaping
    if current_gameboard['num_turns'] < 10:
        print(f'Panther trying to escape from top edges of the board, since turns {current_gameboard["num_turns"]} < 10')
        target = np.random.choice(top_edges_escape)
        # cur_loc = player.current_position.location_name
        cur_loc = path[-1]
        shortest_path = nx.shortest_path(G, source=cur_loc, target=target)
        rest_move = current_gameboard['max_panther_path_length'] - (len(path) - 1)
        path += shortest_path[1:1+rest_move]

    # At this moment, either move slow or stop for hiding on the board
    # but we should slowly move upward for chance to escape
    else:
        print(f'Panther trying to hide himself for undamaged, since turns {current_gameboard["num_turns"]} >= 10')
        chance2escape = ['A', 'B', 'C']
        if any([1 if region in player.current_position.location_name else 0 for region in chance2escape]):
            # since we are close to top edges, move slow/fast for increasing chance to escape
            speed_decision = 1 if np.random.uniform(0, 1) < 0.5 else 2
            target = np.random.choice(top_edges_escape)
            cur_loc = player.current_position.location_name
            shortest_path = nx.shortest_path(G, source=cur_loc, target=target)
            path += shortest_path[1:speed_decision + 1]
        else:
            # since still far away from region ABC, the best way is to hide on the board
            print(f'Panther trying to hide somewhere, and currently at location {player.current_position.location_name}')
            speed_decision = 1 if np.random.uniform(0, 1) < 0.5 else 0
            path = _random_walk(current_gameboard, path, speed_decision)

    # If there is rest movement and the escape location nearby, we could escape at this time
    if current_gameboard['max_panther_path_length'] - (len(path) - 1) > 0:
        could_escape, escape_loc = _check_escape_condition(current_gameboard, path)
        if could_escape:
            print(f'Plark has chance to escape from location {path[-1]}')
            path.append(escape_loc.location_name)
            params['panther_path'] = path
            return move_panther, params  # time to escape.

    params['panther_path'] = path
    return move_panther, params


def _random_walk(current_gameboard, path, move_distance):
    while len(path) - 1 < move_distance:
        m = list(current_gameboard['location_map'][path[-1]].neighbors)
        np.random.shuffle(m)
        for candidate in m:
            if candidate.location_name not in path:
                next_move = candidate
        path.append(next_move.location_name)
    return path


def _check_escape_condition(current_gameboard, path):
    for neighbor in current_gameboard['location_map'][path[-1]].neighbors:
        if neighbor.location_name == 'escape':
            return True, neighbor
    return False, None


def make_bloodhound_phase_move(player, current_gameboard, allowable_actions, code):
    if player.player_class != 'Panther':
        print('Non-Panther is trying to make bloodhound phase move...')
        raise Exception

    print('change explosion to disturbed water, or remove disturbed water')
    update_water_counters(current_gameboard)

    if move_update_torpedoes in allowable_actions:
        print('executing move_update_torpedoes...')
        params = dict()
        params['current_gameboard'] = current_gameboard
        return move_update_torpedoes, params

    if null_action in allowable_actions:
        print('returning null_action...')
        return null_action, dict()
    else:
        print('something has gone wrong, we should not be here')
        raise Exception


def initialization_routine(agent, current_gameboard):
    if agent.agent_type == 'Panther':
        agent.init_position = '0503H'
        # agent.init_position = '0101B'
    elif agent.agent_type == 'Pelican':
        agent.init_position = '0405C'
        agent.init_weapons_bay = dict()
        agent.init_weapons_bay['sonobuoy_count'] = 12
        agent.init_weapons_bay['torpedo_count'] = 6

    else:
        print('agent has unrecognized type. Cannot initialize position')
        raise Exception


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
    ans['agent_type'] = 'Panther'
    return ans


decision_agent_methods = _build_decision_agent_methods_dict() # this is the main data structure that is needed by gameplay
