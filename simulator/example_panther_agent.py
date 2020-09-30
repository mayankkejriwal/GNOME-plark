from simulator.action_choices import *
import numpy as np

"""
If you're a pelican, you only need to implement the first function until further notice.
Leave the other functions as is, or copy them over to your new agent.

If you're a panther, you should implement only the panther phase until further notice.
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

    print('plark speed has been determined to be ',speed)
    det_range = current_gameboard['detection_range'][speed]
    print('Hence, detection range is ',str(det_range))
    plark_location = player.current_position

    s_updates = dict()

    for weapon_name, weapon in current_gameboard['weapons_inventory'].items():
        if weapon.location is None or weapon.weapon_class == 'torpedo':
            continue
        else:
            cur_weapon_location = weapon.location
            print('we need to determine new status for sonobuoy ',weapon_name,' which is currently at ',cur_weapon_location.location_name)
            if plark_location.calculate_distance(current_gameboard, cur_weapon_location) <= det_range:
                print('sonobuoy is within plark det_range. updating to hot...')
                s_updates[weapon_name] = 'hot'
                continue
            else:
                dis = cur_weapon_location.locate_nearest_disturbed_water(current_gameboard)
                if dis and dis.calculate_distance(current_gameboard, cur_weapon_location) <= current_gameboard['sonobuoy_disturbed_water_threshold']:
                    print('sonobuoy is within sonobuoy_disturbed_water_threshold of disturbed water. updating to hot...')
                    s_updates[weapon_name] = 'hot'
                    continue

                expl = cur_weapon_location.locate_nearest_underwater_explosion(current_gameboard)
                if expl and expl.calculate_distance(current_gameboard, cur_weapon_location) <= current_gameboard['sonobuoy_underwater_explosion_threshold']:
                    print('sonobuoy is within sonobuoy_underwater_explosion_threshold of disturbed water. updating to hot...')
                    s_updates[weapon_name] = 'hot'
                    continue

                print('sonobuoy stays cold, or is flipped from hot to cold...')
                s_updates[weapon_name] = 'cold'

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

    path = list()
    path.append(player.current_position.location_name)
    params = dict()
    # player, current_gameboard, pelican_path, weapons_dict
    params['player'] = player
    params['current_gameboard'] = current_gameboard

    while len(path) < current_gameboard['max_panther_path_length']:
        m = list(current_gameboard['location_map'][path[-1]].neighbors)
        for i in m:
            if i.location_name == 'escape':
                print(player.player_name,' has a chance to escape...')
                path.append(m[0].location_name)
                params['panther_path'] = path
                return move_panther, params # time to escape.
        np.random.shuffle(m)
        print('appending ',m[0].location_name,' to path of ',player.player_name)
        path.append(m[0].location_name)

    params['panther_path'] = path
    return move_panther, params


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
        # agent.init_position = '0503H'
        agent.init_position = '0501B'
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
