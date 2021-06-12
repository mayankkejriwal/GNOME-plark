from simulator.action_choices import *
import numpy as np
import networkx as nx

"""
If you're a pelican, you only need to implement the first function until further notice.
Leave the other functions as is, or copy them over to your new agent.

If you're a panther, you should implement only the panther phase until further notice.
"""

# MAD_check = False
# MAD_check_turn = 0

def make_pelican_phase_move(player, current_gameboard, allowable_actions, code):
    """
    Agent first drops 10 MPs around the starting area for Panther, then drops 6 more at 907G, 305H, 308H, 707H, 704H, and 107J.
    at beginning of turn, if any MP are hot, then we drop one BH on the hot MP.
    if MM is on, and still have MP, drop MPs along last turn path. If No MP, then move 5 hex a turn along last turn path.

    if no hot MP or MM after all MP are dropped, then spend rest of turns checking every hex in beginning once, until it sees MM,
    once MM is on, check last turn path 5 hex a turn and see if MM is still on to find Panther, once location is thought to be found. drop 1 BH.
    repeat.

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

    move_lookup = {
        '0508J': '0507J', '0507J': '0506J', '0506J': '0505J', '0505J': '0404J', '0404J': '0304J', '0304J': '0203J',
        '0203J': '0103J', '0103J': '1002H', '1002H': '0902H', '0902H': '0801H', '0801H': '0701H', '0701H': '0610E',
        '0610E': '0510E', '0510E': '0410E', '0410E': '0301H', '0301H': '0201H', '0201H': '0102H', '0102H': '1002G',
        '1002G': '0903G', '0903G': '0803G', '0803G': '0704G', '0704G': '0604G', '0604G': '0505G', '0505G': '0506G',
        '0506G': '0507G', '0507G': '0508G', '0508G': '0608G', '0608G': '0708G', '0708G': '0807G', '0807G': '0907G',
        '0907G': '0906G', '0906G': '1005G', '1005G': '0105H', '0105H': '0204H', '0204H': '0304H', '0304H': '0305H',
        '0305H': '0306H', '0306H': '0307H', '0307H': '0406H', '0406H': '0507H', '0507H': '0606H', '0606H': '0707H',
        '0707H': '0706H', '0706H': '0705H', '0705H': '0704H', '0704H': '0804H', '0804H': '0905H', '0905H': '1005H',
        '1005H': '0106J', '0106J': '0107J', '0107J': '1006H', '1006H': '0906H', '0906H': '0805H', '0805H': '0806H',
        '0806H': '0807H', '0807H': '0808H', '0808H': '0708H', '0708H': '0607H', '0607H': '0508H', '0508H': '0407H',
        '0407H': '0308H', '0308H': '0207H', '0207H': '0206H', '0206H': '0205H', '0205H': '0106H', '0106H': '1006G',
        '1006G': '1007G', '1007G': '1008G', '1008G': '0908G', '0908G': '0808G', '0808G': '0709G', '0709G': '0609G',
        '0609G': '0710G', '0710G': '0809G', '0809G': '0909G', '0909G': '0910G', '0910G': '1009G', '1009G': '0110H',
        '0110H': '0109H', '0109H': '0108H', '0108H': '0208H', '0208H': '0209H', '0209H': '0310H', '0310H': '0309H',
        '0309H': '0409H', '0409H': '0408H', '0408H': '0509H', '0509H': '0510H', '0510H': '0609H', '0609H': '0608H',
        '0608H': '0709H', '0709H': '0710H', '0710H': '0809H', '0809H': '0910H', '0910H': '0909H', '0909H': '0908H',
        '0908H': '0907H', '0907H': '1007H', '1007H': '1008H', '1008H': '1009H', '1009H': '0110J', '0110J': '0109J',
        '0109J': '0108J', '0108J': '0208J', '0208J': '0209J', '0209J': '0310J', '0310J': '0409J', '0409J': '0309J',
        '0309J': '0308J', '0308J': '0408J', '0408J': '0407J', '0407J': '0307J', '0307J': '0207J', '0207J': '0206J',
        '0206J': '0306J', '0306J': '0406J', '0406J': '0405J', '0405J': '0305J', '0305J': '0205J', '0205J': '0204J',
        '0204J': '0105J', '0105J': '0104J', '0104J': '1004H', '1004H': '1003H', '1003H': '0904H', '0904H': '0903H',
        '0903H': '0803H', '0803H': '0802H', '0802H': '0703H', '0703H': '0702H', '0702H': '0601H', '0601H': '0602H',
        '0602H': '0603H', '0603H': '0604H', '0604H': '0605H', '0605H': '0506H', '0506H': '0405H', '0405H': '0404H',
        '0404H': '0505H', '0505H': '0504H', '0504H': '0403H', '0403H': '0503H', '0503H': '0402H', '0402H': '0502H',
        '0502H': '0501H', '0501H': '0401H', '0401H': '0302H', '0302H': '0303H', '0303H': '0202H', '0202H': '0203H',
        '0203H': '0103H', '0103H': '0104H', '0104H': '1003G', '1003G': '1004G', '1004G': '0904G', '0904G': '0905G',
        '0905G': '0804G', '0804G': '0805G', '0805G': '0705G', '0705G': '0605G', '0605G': '0606G', '0606G': '0607G',
        '0607G': '0707G', '0707G': '0806G', '0806G': '0706G', '0706G': '0706G'
    }
    curr_pos = player.current_position.location_name

    while len(path) < current_gameboard['max_pelican_path_length']:

        HMP = False
        # MPs = player.weapons_bay['sonobuoy']
        MPs = current_gameboard['weapons_inventory']
        for MP in MPs:
            if MPs[MP].state == 'hot':
                HMP = True
                HMP_loc = MPs[MP].location.location_name
                shortest_path = nx.shortest_path(current_gameboard['game_graph'], source=curr_pos, target=HMP_loc)

                curr_pos = HMP_loc
                shortest_path.pop(0) # TODO: test if 2 HMP
                path.extend(shortest_path)
                path = path[:20]

                if player.weapons_bay['torpedo'] and HMP_loc not in weapons_dict and HMP_loc in path: #TODO: also only drop if no torpedo/distrubed water is present (not just weapon_bay, since i think WB is onoly for this turn)
                    weapons_dict[path[-1]] = set()
                    # weapons_dict[path[-1]] = set()
                    # weapons_dict[path[-1]].add(player.eject_torpedo().weapon_name)
                    weapons_dict[path[-1]].add(player.eject_torpedo().weapon_name)
                    print('we will drop torpedo ', weapons_dict[path[-1]], ' on location ', path[-1])
        if HMP:
            # only finish turn early if BH are dropped on HMP, otherwise, spend all 20 moves moving and dropping MP
            break

        MP_spot = {'0508J', '0505J', '0203J', '0902H', '0610E', '0301H', '1002G', '704G',
                   '0506G', '0608G', '0906G', '0304H', '0307H', '0707H', '0704H', '0107J'}
        if not HMP:
            if player.MAD: # or MAD_check:
                # MAD_check = True
                # get path of last turn in reverse for a list
                last_turn = player.path_history[-1].copy()
                last_turn.reverse()

                # if we have MPs, drop on the last path, then end turn to get HMPs
                # every 3 steps, drop at location last_turn[i]
                if player.weapons_bay['sonobuoy']: # first check is used so we only drop BHs if we don't have MPs
                    for i in range(0, len(last_turn), 3):
                        if player.weapons_bay['sonobuoy']: # second check is to not crash when out of MPs
                            weapons_dict[last_turn[i]] = set()
                            weapons_dict[last_turn[i]].add(player.eject_sonobuoy().weapon_name)
                            print('we will drop sonobuoy ', weapons_dict[last_turn[i]], ' on location ', last_turn[i])

                # if no MPs, then we just drop BHs
                elif player.weapons_bay['torpedo']: # first check is used so we only drop BHs if we don't have MPs
                # every 5 steps, drop at location last_turn[i]
                    for i in range(0, len(last_turn), 5):
                        if player.weapons_bay['torpedo']: # second check is to not crash when out of BHs
                            weapons_dict[last_turn[i]] = set()
                            weapons_dict[last_turn[i]].add(player.eject_torpedo().weapon_name)
                            print('we will drop torpedo ', weapons_dict[last_turn[i]], ' on location ', last_turn[i])

                # move - add last turn's path in reverse into this turn's path
                path = list()
                path.extend(last_turn)

            elif any(x == curr_pos for x in MP_spot):
                if player.weapons_bay['sonobuoy']:
                    weapons_dict[path[-1]] = set()
                    weapons_dict[path[-1]].add(player.eject_sonobuoy().weapon_name)
                    print('we will drop sonobuoy ',weapons_dict[path[-1]],' on location ',path[-1])

            if not player.MAD:
                next_move = move_lookup[curr_pos]
                curr_pos = next_move
                path.append(next_move)

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
        agent.init_position = '503H'
    elif agent.agent_type == 'Pelican':
        agent.init_position = '0508J'
        agent.init_weapons_bay = dict()
        agent.init_weapons_bay['sonobuoy_count'] = 12
        agent.init_weapons_bay['torpedo_count'] = 15

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
