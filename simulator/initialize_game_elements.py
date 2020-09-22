"""
The only public facing function is initialize_board. All _initialize_* functions are only for internal use. If you
want to play around, you could always implement your _initialize functions and replace accordingly in initialize_board!
"""

from simulator.player import Player
from simulator.location import Location
from simulator.auxiliary_functions import generate_default_gameboard_graph
import networkx as nx


def initialize_board(player_decision_agents):

    game_elements = dict()

    # _initialize_func(game_elements)
    _initialize_players(game_elements, player_decision_agents)
    print('finished initializing player data structures...')

    _initialize_game_history_structs(game_elements)
    print('finished initializing game history data structures...')

    _initialize_locations(game_elements)
    print('finished initializing location data structures...')

    game_elements['max_pelican_path_length'] = 10
    game_elements['max_panther_path_length'] = 2

    game_elements['weapons_inventory'] = dict() # key is the weapon name, value is the weapon instance
    game_elements['bingo_limit'] = 36
    game_elements['player_turn_sequence'] = list() # list of player-instances that are making moves, to track that its all going in the right order

    game_elements['detection_range'] = dict() # recall that this is used for both the sonobuoys and torpedoes
    game_elements['detection_range']['stopped'] = 1
    game_elements['detection_range']['slow'] = 3
    game_elements['detection_range']['fast'] = 5

    game_elements['torpedo_speed'] = dict()
    game_elements['torpedo_detection_range'] = 5 # the range at which one torpedo can detect another
    game_elements['torpedo_listening_range'] = 5 # the listening range should never be lower than the detection range.
    game_elements['torpedo_speed']['first_turn'] = 3
    game_elements['torpedo_speed']['second_turn'] = 2

    game_elements['plark_speed'] = dict()
    game_elements['plark_speed']['stopped'] = 0
    game_elements['plark_speed']['slow'] = 1
    game_elements['plark_speed']['fast'] = 2

    game_elements['sonobuoy_disturbed_water_threshold'] = 5
    game_elements['sonobuoy_underwater_explosion_threshold'] = 10

    return game_elements


# def serialize_board(game_elements, output_file=None): # to come
#     json_dict = dict()
#
#     if output_file:
#         pass
#     else:
#         print(json_dict)


# def _initialize_func(game_elements): # instantiate, implement and expand as necessary
#     return None


def _initialize_locations(game_elements): # instantiate, implement and expand as necessary
    # first let's populate without neighbors or special position flags
    game_graph = generate_default_gameboard_graph()
    game_elements['game_graph'] = game_graph

    game_elements['location_map'] = dict()
    for i in range(1,11):
        for j in range(1,11):
            for k in ['A','B','C','D','E','F','G','H','J']: # note that there is no I, we are following the submaps as
                # stated in the v1.4.pdf doc.
                location_name = ""
                if i >= 10:
                    location_name += str(i)
                else:
                    location_name += ('0' + str(i))

                if j >= 10:
                    location_name += str(j)
                else:
                    location_name += ('0' + str(j))

                location_name += k
                game_elements['location_map'][location_name] = Location(location_name=location_name,submap=k)

    # now let's populate the neighbors
    for k,v in game_elements['location_map'].items():
        neighs = set([game_elements['location_map'][n] for n in game_graph.neighbors(k)])
        v.update_neighbors(neighbors=neighs)


    # now we'll populate special position flags
    for lname,location in game_elements['location_map'].items():
        special_flags = set()
        x = int(location.location_name[0:2])
        y = int(location.location_name[2:4])
        smap = location.submap

        # let's check for edges first
        if x%2 != 0 and smap in {'A','B','C'} and y==1:
            special_flags.add('top_edge')
        if smap in {'G','H','J'} and y==10:
            special_flags.add('bottom_edge')

        if smap in {'A','D','G'} and x==1:
            special_flags.add('left_edge')

        if smap in {'F','J','C'} and x==10:
            special_flags.add('right_edge')


        # now let's check for corners
        if 'top_edge' in location.special_position_flags and 'left_edge' in location.special_position_flags:
            special_flags.add('top_left_corner')

            location.update_neighbors({game_elements['location_map']['0102A'],game_elements['location_map']['0201A']})
        if 'top_edge' in location.special_position_flags and 'right_edge' in location.special_position_flags:
            special_flags.add('top_right_corner')
            print('top right corner should not exist...')
            raise Exception
        if 'bottom_edge' in location.special_position_flags and 'left_edge' in location.special_position_flags:
            special_flags.add('bottom_left_corner')

            location.update_neighbors({game_elements['location_map']['0109G'], game_elements['location_map']['0209G'],
                                       game_elements['location_map']['0210G']})
        if 'bottom_edge' in location.special_position_flags and 'right_edge' in location.special_position_flags:
            special_flags.add('bottom_right_corner')

            location.update_neighbors({game_elements['location_map']['0910J'], game_elements['location_map']['1009J']})


        # now let's check for the panther zone
        if location.calculate_distance(game_elements,game_elements['location_map']['0510H']) <= 10:
            special_flags.add('panther_zone')

        location.update_special_position_flags(special_flags)


    escape = Location('escape', None, None) #important to remember that this is NOT in the graph, and has no neighbors of its own
    escape.num_neighbors = 0
    for lname, location in game_elements['location_map'].items():
        if 'top_edge' in location.special_position_flags:
            location.neighbors.add(escape)
            location.num_neighbors += 1


    # make sure to do a sanity check.
    _location_sanity_test_neighbors(game_elements)


def _location_sanity_test_neighbors(game_elements):
    lmap = game_elements['location_map']
    flag = True

    # let's start with the board corners
    if not lmap['0110G'].serialize_neighbors()==set(['0109G','0209G','0210G']):
        lmap['0110G']._print_location_data()
        flag = False

    if not lmap['0101A'].serialize_neighbors()==set(['0201A','0102A']):
        lmap['0101A']._print_location_data()
        flag = False


    if not lmap['1010J'].serialize_neighbors()==set(['0910J','1009J']):
        lmap['1010J']._print_location_data()
        flag = False


    if not lmap['1001C'].serialize_neighbors()==set(['0902C','1002C','0901C']):
        lmap['1001C']._print_location_data()
        flag = False

    # left edge
    if not lmap['0105A'].serialize_neighbors() == set(['0104A', '0204A', '0205A', '0106A']):
        lmap['0105A']._print_location_data()
        flag = False

    if not lmap['0105D'].serialize_neighbors() == set(['0104D', '0204D', '0205D', '0106D']):
        lmap['0105D']._print_location_data()
        flag = False

    if not lmap['0105G'].serialize_neighbors() == set(['0104G', '0204G', '0205G', '0106G']):
        lmap['0105G']._print_location_data()

    if not lmap['0110A'].serialize_neighbors() == set(['0109A', '0209A', '0210A', '0101D']):
        lmap['0110A']._print_location_data()
        flag = False

    if not lmap['0210A'].serialize_neighbors() == set(['0110A', '0101D', '0209A', '0310A','0301D','0201D']):
        lmap['0210A']._print_location_data()
        flag = False

    if not lmap['0101D'].serialize_neighbors() == set(['0110A', '0210A', '0201D', '0102D']):
        lmap['0101D']._print_location_data()
        flag = False

    if not lmap['0201D'].serialize_neighbors() == set(['0210A','0101D','0301D', '0302D', '0202D', '0102D']):
        lmap['0201D']._print_location_data()
        flag = False

    if flag:
        print('all tests have succeeded.')
    else:
        print('at least one test has failed. that\'s all I know')

    # game_elements['location_map']['0101A']._print_location_data()
    # print()
    # game_elements['location_map']['0110G']._print_location_data()
    # print()
    # game_elements['location_map']['1010J']._print_location_data()
    # print()
    # game_elements['location_map']['1001C']._print_location_data()
    # print()
    # game_elements['location_map']['0101B']._print_location_data()
    # print()
    # game_elements['location_map']['1001B']._print_location_data()
    # print()
    # game_elements['location_map']['1010A']._print_location_data()
    # print()
    # game_elements['location_map']['0108D']._print_location_data()
    # print()
    # game_elements['location_map']['1010F']._print_location_data()
    # print()
    # game_elements['location_map']['1009J']._print_location_data()


def _initialize_players(game_elements, player_decision_agents):
    players = list()
    # players.append(dict())
    # player_dict = game_schema['players']['player_states']
    for player in ['pelican','panther']:
        player_args = dict()
        player_args['player_name'] = player
        if player == 'pelican':
            player_args['player_class'] = 'Pelican'
        elif player == 'panther':
            player_args['player_class'] = 'Panther'
        player_args['agent'] = player_decision_agents[player]
        players.append(Player(**player_args))

    game_elements['players'] = players


def _initialize_game_history_structs(game_elements):
    game_elements['history'] = dict()
    game_elements['history']['function'] = list()
    game_elements['history']['param'] = list()
    game_elements['history']['return'] = list()
