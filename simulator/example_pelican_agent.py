from simulator.action_choices import *
import numpy as np
"""
If you're a pelican, you only need to implement the first function until further notice.
Leave the other functions as is, or copy them over to your new agent.

If you're a panther, you should implement only the panther phase until further notice.
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
    while len(path) < current_gameboard['max_pelican_path_length']:
        m = [i for i in current_gameboard['location_map'][path[-1]].neighbors if i.location_name != 'escape'] # pelican can't leave the board
        np.random.shuffle(m)
        print('appending location ',m[0].location_name,' to return-path of ',player.player_name)
        path.append(m[0].location_name)

        if len(path) == 5:
            if player.weapons_bay['torpedo']:
                weapons_dict[path[-1]] = set()
                weapons_dict[path[-1]].add(player.eject_torpedo().weapon_name)
                print('we will drop torpedo ', weapons_dict[path[-1]], ' on location ', path[-1])

            elif player.weapons_bay['sonobuoy']:
                weapons_dict[path[-1]] = set()
                weapons_dict[path[-1]].add(player.eject_sonobuoy().weapon_name)
                print('we will drop sonobuoy ',weapons_dict[path[-1]],' on location ',path[-1])




    params = dict()
    #player, current_gameboard, pelican_path, weapons_dict
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
    ans['agent_type'] = 'Pelican'
    return ans


decision_agent_methods = _build_decision_agent_methods_dict() # this is the main data structure that is needed by gameplay
