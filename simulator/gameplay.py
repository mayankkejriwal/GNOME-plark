
import numpy as np
# import json
import simulator.initialize_game_elements as initialize_game_elements
from simulator.flag_config import flag_config_dict
from simulator.utility_actions import *
from simulator.weapon import Sonobuoy,Torpedo
import simulator.example_pelican_agent as example_pelican_agent
import simulator.example_panther_agent as example_panther_agent
from simulator.agent import Agent

def simulate_game_instance(game_elements, history_log_file=None, np_seed=2):
    """
    Simulate a game instance.
    :param game_elements: The dict output by set_up_board
    :param np_seed: The numpy seed to use to control randomness.
    :return: None

    Currently, this function is defined for the default game. We reserve the right to modify as we retrofit
    this package to support novelty.
    """
    print('we are now in simulate_game_instance. The random seed is ',str(np_seed))
    np.random.seed(np_seed)
    winner = None
    turns = 0
    current_phase = 'pelican_phase'

    for p in game_elements['players']:
        if p.player_class == 'Pelican':
            print('setting status of ',p.player_name,' to current.')
            p.status = 'current'

    while True:
        if current_phase == 'pelican_phase':
            print('current phase is pelican')

            for p in game_elements['players']:
                if p.status == 'current':
                    print('resetting MAD to false for ',p.player_name)
                    p.manipulate_MAD(new_MAD=False)

                    print(p.player_name,' is making pelican phase moves.')
                    p.make_pelican_phase_moves(game_elements)

                    print('appending ',p.player_name, ' to player_turn_sequence')
                    game_elements['player_turn_sequence'].append(p)

                    print('setting status of ', p.player_name, ' to waiting')
                    p.status = 'waiting'

            for p in game_elements['players']:
                if p.player_class == 'Panther':
                    print('setting status of ', p.player_name, ' to current.')
                    p.status = 'current'
            current_phase = 'madman_phase'

        elif current_phase == 'madman_phase':
            print('current phase is madman')

            for p in game_elements['players']:
                if p.status == 'current':
                    print(p.player_name, ' is making madman phase moves.')
                    p.make_madman_phase_moves(game_elements)

                    print('appending ', p.player_name, ' to player_turn_sequence')
                    game_elements['player_turn_sequence'].append(p)
            current_phase = 'maypole_phase'


        elif current_phase == 'maypole_phase':
            print('current phase is maypole')

            for p in game_elements['players']:
                if p.status == 'current':
                    print(p.player_name, ' is making maypole phase moves.')
                    p.make_maypole_phase_moves(game_elements)

                    print('appending ', p.player_name, ' to player_turn_sequence')
                    game_elements['player_turn_sequence'].append(p)
            current_phase = 'panther_phase'


        elif current_phase == 'panther_phase':
            print('current phase is panther')
            for p in game_elements['players']:
                if p.status == 'current':
                    print(p.player_name, ' is making panther phase moves.')
                    p.make_panther_phase_moves(game_elements)

                    print('appending ', p.player_name, ' to player_turn_sequence')
                    game_elements['player_turn_sequence'].append(p)
            if has_plark_escaped(game_elements):
                winner = check_for_winner(game_elements)
                break
            current_phase = 'bloodhound_phase'


        elif current_phase == 'bloodhound_phase':
            print('current phase is bloodhound')
            for p in game_elements['players']:
                if p.status == 'current':
                    print(p.player_name, ' is making bloodhound phase moves.')
                    p.make_bloodhound_phase_moves(game_elements)

                    print('appending ', p.player_name, ' to player_turn_sequence')
                    game_elements['player_turn_sequence'].append(p)

                    print('setting status of ', p.player_name, ' to waiting')
                    p.status = 'waiting'
            if is_plark_sunk(game_elements):
                winner = check_for_winner(game_elements) # has to be the pelican, but let's make sure.
                break

            for p in game_elements['players']:
                if p.player_class == 'Pelican':
                    print('setting status of ', p.player_name, ' to current')
                    p.status = 'current'

            current_phase = 'pelican_phase'
            turns += 1
            print('number of turns passed is ',str(turns))

        if turns >= game_elements['bingo_limit']:
            winner = check_for_winner(game_elements)
            break

        if check_for_winchester(game_elements):
            winner = check_for_winner(game_elements)
            break



    if winner is not None:
        print(winner.player_name,' is the winner.')
    else:
        print("There is no winner. It's a draw")

    return winner


def set_up_board(player_decision_agents):
    return initialize_game_elements.initialize_board(player_decision_agents)


def initialize_player_data(game_elements):
    for p in game_elements['players']:

        if p.player_class == 'Pelican':
            print(p.player_name,' position is being initialized to ',p.agent.init_position)
            p.current_position = game_elements['location_map'][p.agent.init_position]
            p.weapons_bay = dict()
            for k,v in p.agent.init_weapons_bay.items():
                if k == 'sonobuoy_count':
                    for i in range(0,v):
                        if 'sonobuoy' not in p.weapons_bay:
                            p.weapons_bay['sonobuoy'] = set()
                        s_weapon = Sonobuoy(weapon_name='s'+str(i+1),player=p)
                        print(p.player_name, 'is getting sonobuoy ',s_weapon.weapon_name,' in their weapons bay.')
                        p.weapons_bay['sonobuoy'].add(s_weapon)
                        game_elements['weapons_inventory']['s'+str(i+1)] = s_weapon
                elif k == 'torpedo_count':
                    for i in range(0,v):
                        if 'torpedo' not in p.weapons_bay:
                            p.weapons_bay['torpedo'] = set()
                        t_weapon = Torpedo(weapon_name='t'+str(i+1),player=p)
                        print(p.player_name, 'is getting torpedo ', t_weapon.weapon_name, ' in their weapons bay.')
                        p.weapons_bay['torpedo'].add(t_weapon)
                        game_elements['weapons_inventory']['t'+str(i+1)] = t_weapon
        elif p.player_class == 'Panther':
            if 'panther_zone' not in game_elements['location_map'][p.agent.init_position].special_position_flags:
                print('panther is not starting from an allowed position. Raising exception')
                raise Exception
            p.current_position = game_elements['location_map'][p.agent.init_position]
            print(p.player_name, ' position is initialized to ',p.agent.init_position)
            if p.agent.init_weapons_bay is not None:
                print('panther is not supposed to have weapons. Raising exception')
                raise Exception
            print('initializing damage_status of ',p.player_name,' to undamaged.')
            p.damage_status = 'undamaged'



# def inject_novelty(current_gameboard, novelty_schema=None):
#     pass


def play_game():
    """
    Use this function if you want to test a single game instance and control lots of things. For experiments, we will directly
    call some of the functions in gameplay from test_harness.py.

    This is where everything begins. Assign decision agents to your players, set up the board and start simulating! You can
    control any number of players you like, and assign the rest to the simple agent.

    :return: String. the name of the player who won the game, if there was a winner, otherwise None.
    """


    player_decision_agents = dict()

    player_decision_agents['pelican'] = Agent(**example_pelican_agent.decision_agent_methods)
    player_decision_agents['panther'] = Agent(**example_panther_agent.decision_agent_methods)

    game_elements = set_up_board(player_decision_agents) # we have decided not to support a schema
    print('finished setting up the board')
    # initialize_game_elements.serialize_board(game_elements, output_file=None)
    # return
    # inject_novelty(game_elements)


    if player_decision_agents['pelican'].startup(game_elements) == flag_config_dict['failure_code'] or \
            player_decision_agents['panther'].startup(game_elements) == flag_config_dict['failure_code']:
        print('something went wrong, agents have not been successfully started...')
        return None
    else:
        print('agents have been successfully started')
        initialize_player_data(game_elements)
        print('finished initializing player data. Entering simulation...')
        winner = simulate_game_instance(game_elements)

        if player_decision_agents['pelican'].shutdown() == flag_config_dict['failure_code'] or \
            player_decision_agents['panther'].shutdown() == flag_config_dict['failure_code']:
            print('something went wrong, agents have not successfully shut down...')
            return None
        else:
            print("All player agents have been shutdown. ")
            print("GAME OVER")
            print(winner.player_name)
            return winner


# def play_game_in_tournament(game_seed, inject_novelty_function=None):
#     print('seed used: ' + str(game_seed))
#     player_decision_agents = dict()
#
#     # player_decision_agents['player_1'] = Agent(**simple_decision_agent_1.decision_agent_methods)
#     # player_decision_agents['player_2'] = Agent(**simple_decision_agent_1.decision_agent_methods)
#
#
#     game_elements = set_up_board(player_decision_agents)
#
#
#     if inject_novelty_function:
#         inject_novelty_function(game_elements)
#
#     if player_decision_agents['pelican'].startup(game_elements) == flag_config_dict['failure_code'] or \
#             player_decision_agents['panther'].startup(game_elements) == flag_config_dict['failure_code']:
#         print("Error in initializing agents. Cannot play the game.")
#         return None
#     else:
#         print("Sucessfully initialized all player agents.")
#         winner = simulate_game_instance(game_elements, history_log_file=None, np_seed=game_seed)
#         if player_decision_agents['pelican'].shutdown() == flag_config_dict['failure_code'] or \
#                 player_decision_agents['panther'].shutdown() == flag_config_dict['failure_code']:
#             print("Error in agent shutdown.")
#             return None
#         else:
#             print("All player agents have been shutdown. ")
#             print("GAME OVER")
#             return winner


play_game()
