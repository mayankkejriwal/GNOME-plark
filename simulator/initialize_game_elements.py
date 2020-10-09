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

    game_elements['max_pelican_path_length'] = 20
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

    # weapon inventory slot 24
    # torpedo 2 sonobuoy 1

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

    game_elements['location_map']['escape'] = escape

    # make sure to do a sanity check.
    _location_sanity_test_neighbors(game_elements)


def _location_sanity_test_neighbors(game_elements):
    lmap = game_elements['location_map']
    flag = True

    # let's start with the board corners
    if not lmap['0110G'].serialize_neighbors()==set(['0109G','0209G','0210G']):
        lmap['0110G']._print_location_data()
        flag = False

    if not lmap['0101A'].serialize_neighbors()==set(['0201A','0102A','escape']):
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

    regions = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J')
    top_edges = ('0101', '0201', '0301', '0401', '0501', '0601', '0701', '0801', '0901', '1001')
    bottom_edge = ('0110', '0210', '0310', '0410', '0510', '0610', '0710', '0810', '0910', '1010')
    left_edge = ('0101', '0102', '0103', '0104', '0105', '0106', '0107', '0108', '0109', '0110')
    right_edge = ('1001', '1002', '1003', '1004', '1005', '1006', '1007', '1008', '1009', '1010')

    """ERROR FOUND like
    0101B {'0102B', 'escape'}
    0101C {'0102C', 'escape'}
    """
    test_dict = _get_sanity_neighbors()  # 0,1,2,3 --> top, bottom, left, right respectively
    for edges, name in zip((top_edges, bottom_edge, left_edge, right_edge), ('Top', 'Bottom', 'Left', 'Right')):
        location2neighbors = test_dict[name]
        print(f'Testing for {name} borders of each region...')
        for region in regions:
            for edge_number in edges:
                location_name = edge_number + region
                if lmap[location_name].serialize_neighbors() != location2neighbors[location_name]:
                    print(f'Location {location_name} lacks neighbors {location2neighbors[location_name] - lmap[location_name].serialize_neighbors()}')
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


def _get_sanity_neighbors():
    top2neighbors = {
        "0101A": {'0102A', 'escape', '0201A'},
        "0201A": {'0302A', '0102A', '0301A', '0202A', '0101A'},
        "0301A": {'0302A', '0401A', 'escape', '0201A'},
        "0401A": {'0501A', '0302A', '0502A', '0301A', '0402A'},
        "0501A": {'0401A', '0601A', 'escape', '0502A'},
        "0601A": {'0501A', '0602A', '0502A', '0701A', '0702A'},
        "0701A": {'0702A', '0801A', 'escape', '0601A'},
        "0801A": {'0701A', '0902A', '0901A', '0702A', '0802A'},
        "0901A": {'escape', '0801A', '0902A', '1001A'},
        "1001A": {'0902A', '1002A', '0901A', '0102B', '0101B'},
        "0101B": {'0102B', 'escape', '1001A', '0201B'},
        "0201B": {'0302B', '0301B', '0102B', '0202B', '0101B'},
        "0301B": {'0401B', '0201B', 'escape', '0302B'},
        "0401B": {'0301B', '0402B', '0501B', '0502B', '0302B'},
        "0501B": {'0401B', '0601B', 'escape', '0502B'},
        "0601B": {'0501B', '0502B', '0702B', '0602B', '0701B'},
        "0701B": {'0801B', '0601B', '0702B', 'escape'},
        "0801B": {'0702B', '0901B', '0701B', '0802B', '0902B'},
        "0901B": {'0902B', '1001B', 'escape', '0801B'},
        "1001B": {'0102C', '1002B', '0902B', '0901B', '0101C'},
        "0101C": {'0102C', 'escape', '1001B', '0201C'},
        "0201C": {'0102C', '0202C', '0301C', '0302C', '0101C'},
        "0301C": {'0302C', '0201C', 'escape', '0401C'},
        "0401C": {'0302C', '0402C', '0502C', '0501C', '0301C'},
        "0501C": {'escape', '0401C', '0502C', '0601C'},
        "0601C": {'0702C', '0502C', '0501C', '0602C', '0701C'},
        "0701C": {'0702C', '0801C', 'escape', '0601C'},
        "0801C": {'0702C', '0901C', '0701C', '0802C', '0902C'},
        "0901C": {'1001C', '0801C', 'escape', '0902C'},
        "1001C": {'0901C', '0902C', '1002C'},
        "0101D": {'0102D', '0110A', '0210A', '0201D'},
        "0201D": {'0302D', '0101D', '0102D', '0202D', '0210A', '0301D'},
        "0301D": {'0401D', '0302D', '0210A', '0201D', '0310A', '0410A'},
        "0401D": {'0402D', '0302D', '0501D', '0301D', '0502D', '0410A'},
        "0501D": {'0601D', '0401D', '0510A', '0610A', '0502D', '0410A'},
        "0601D": {'0701D', '0602D', '0501D', '0702D', '0610A', '0502D'},
        "0701D": {'0601D', '0810A', '0801D', '0702D', '0710A', '0610A'},
        "0801D": {'0701D', '0802D', '0810A', '0901D', '0702D', '0902D'},
        "0901D": {'1010A', '1001D', '0810A', '0801D', '0902D', '0910A'},
        "1001D": {'1010A', '0901D', '0902D', '1002D', '0102E', '0101E'},
        "0101E": {'1010A', '0110B', '0102E', '0210B', '1001D', '0201E'},
        "0201E": {'0210B', '0202E', '0301E', '0102E', '0302E', '0101E'},
        "0301E": {'0401E', '0302E', '0410B', '0210B', '0310B', '0201E'},
        "0401E": {'0402E', '0501E', '0301E', '0502E', '0410B', '0302E'},
        "0501E": {'0401E', '0510B', '0610B', '0410B', '0601E', '0502E'},
        "0601E": {'0602E', '0501E', '0610B', '0702E', '0701E', '0502E'},
        "0701E": {'0710B', '0610B', '0601E', '0801E', '0810B', '0702E'},
        "0801E": {'0901E', '0802E', '0810B', '0902E', '0702E', '0701E'},
        "0901E": {'1010B', '0902E', '1001E', '0801E', '0810B', '0910B'},
        "1001E": {'0901E', '0902E', '1002E', '1010B', '0102F', '0101F'},
        "0101F": {'1010B', '0210C', '0110C', '0102F', '1001E', '0201F'},
        "0201F": {'0202F', '0301F', '0302F', '0210C', '0102F', '0101F'},
        "0301F": {'0310C', '0401F', '0201F', '0302F', '0210C', '0410C'},
        "0401F": {'0301F', '0502F', '0302F', '0410C', '0501F', '0402F'},
        "0501F": {'0510C', '0502F', '0401F', '0601F', '0610C', '0410C'},
        "0601F": {'0702F', '0602F', '0502F', '0610C', '0501F', '0701F'},
        "0701F": {'0801F', '0710C', '0702F', '0810C', '0601F', '0610C'},
        "0801F": {'0901F', '0702F', '0810C', '0802F', '0902F', '0701F'},
        "0901F": {'0902F', '0801F', '0910C', '1010C', '0810C', '1001F'},
        "1001F": {'1010C', '0901F', '0902F', '1002F'},
        "0101G": {'0110D', '0201G', '0210D', '0102G'},
        "0201G": {'0102G', '0202G', '0302G', '0101G', '0210D', '0301G'},
        "0301G": {'0302G', '0210D', '0410D', '0401G', '0201G', '0310D'},
        "0401G": {'0302G', '0502G', '0410D', '0501G', '0402G', '0301G'},
        "0501G": {'0502G', '0410D', '0601G', '0401G', '0610D', '0510D'},
        "0601G": {'0702G', '0610D', '0701G', '0602G', '0501G', '0502G'},
        "0701G": {'0601G', '0710D', '0801G', '0610D', '0702G', '0810D'},
        "0801G": {'0702G', '0902G', '0701G', '0901G', '0802G', '0810D'},
        "0901G": {'0910D', '1010D', '1001G', '0801G', '0902G', '0810D'},
        "1001G": {'0102H', '0902G', '1002G', '0901G', '1010D', '0101H'},
        "0101H": {'0110E', '1010D', '0102H', '0210E', '1001G', '0201H'},
        "0201H": {'0102H', '0301H', '0302H', '0202H', '0210E', '0101H'},
        "0301H": {'0302H', '0310E', '0410E', '0201H', '0401H', '0210E'},
        "0401H": {'0301H', '0302H', '0502H', '0501H', '0410E', '0402H'},
        "0501H": {'0610E', '0601H', '0510E', '0410E', '0401H', '0502H'},
        "0601H": {'0501H', '0502H', '0701H', '0702H', '0610E', '0602H'},
        "0701H": {'0610E', '0702H', '0601H', '0801H', '0810E', '0710E'},
        "0801H": {'0901H', '0701H', '0902H', '0810E', '0702H', '0802H'},
        "0901H": {'0801H', '0902H', '1001H', '0910E', '0810E', '1010E'},
        "1001H": {'0901H', '1010E', '0902H', '0102J', '1002H', '0101J'},
        "0101J": {'0102J', '1010E', '0110F', '0210F', '1001H', '0201J'},
        "0201J": {'0202J', '0210F', '0102J', '0302J', '0301J', '0101J'},
        "0301J": {'0210F', '0401J', '0410F', '0302J', '0310F', '0201J'},
        "0401J": {'0501J', '0502J', '0302J', '0301J', '0410F', '0402J'},
        "0501J": {'0610F', '0601J', '0401J', '0410F', '0510F', '0502J'},
        "0601J": {'0702J', '0602J', '0501J', '0502J', '0701J', '0610F'},
        "0701J": {'0610F', '0601J', '0702J', '0710F', '0801J', '0810F'},
        "0801J": {'0702J', '0802J', '0902J', '0901J', '0701J', '0810F'},
        "0901J": {'1001J', '1010F', '0910F', '0902J', '0801J', '0810F'},
        "1001J": {'0902J', '1010F', '1002J', '0901J'}
    }

    bottom2neighbors = {
        "0110A": {'0109A', '0210A', '0101D', '0209A'},
        "0210A": {'0110A', '0310A', '0101D', '0209A', '0201D', '0301D'},
        "0310A": {'0309A', '0210A', '0409A', '0209A', '0410A', '0301D'},
        "0410A": {'0310A', '0401D', '0409A', '0501D', '0510A', '0301D'},
        "0510A": {'0610A', '0609A', '0409A', '0501D', '0410A', '0509A'},
        "0610A": {'0609A', '0501D', '0601D', '0510A', '0710A', '0701D'},
        "0710A": {'0709A', '0609A', '0610A', '0810A', '0809A', '0701D'},
        "0810A": {'0801D', '0910A', '0809A', '0710A', '0701D', '0901D'},
        "0910A": {'1010A', '0909A', '1009A', '0810A', '0809A', '0901D'},
        "1010A": {'0101E', '1009A', '0110B', '1001D', '0910A', '0901D'},
        "0110B": {'0109B', '0209B', '1010A', '0101E', '1009A', '0210B'},
        "0210B": {'0310B', '0209B', '0101E', '0110B', '0201E', '0301E'},
        "0310B": {'0209B', '0409B', '0210B', '0309B', '0410B', '0301E'},
        "0410B": {'0401E', '0310B', '0409B', '0501E', '0510B', '0301E'},
        "0510B": {'0610B', '0409B', '0509B', '0501E', '0609B', '0410B'},
        "0610B": {'0601E', '0501E', '0609B', '0510B', '0710B', '0701E'},
        "0710B": {'0610B', '0809B', '0609B', '0810B', '0701E', '0709B'},
        "0810B": {'0910B', '0901E', '0809B', '0701E', '0801E', '0710B'},
        "0910B": {'1009B', '0909B', '0901E', '0809B', '0810B', '1010B'},
        "1010B": {'1009B', '0910B', '0101F', '1001E', '0901E', '0110C'},
        "0110C": {'1009B', '0210C', '0101F', '0209C', '0109C', '1010B'},
        "0210C": {'0201F', '0310C', '0301F', '0101F', '0209C', '0110C'},
        "0310C": {'0210C', '0301F', '0309C', '0209C', '0410C', '0409C'},
        "0410C": {'0501F', '0310C', '0301F', '0510C', '0401F', '0409C'},
        "0510C": {'0501F', '0509C', '0410C', '0609C', '0610C', '0409C'},
        "0610C": {'0501F', '0601F', '0609C', '0710C', '0701F', '0510C'},
        "0710C": {'0809C', '0609C', '0610C', '0709C', '0701F', '0810C'},
        "0810C": {'0901F', '0809C', '0801F', '0710C', '0701F', '0910C'},
        "0910C": {'1010C', '0901F', '0909C', '1009C', '0809C', '0810C'},
        "1010C": {'0901F', '1009C', '0910C', '1001F'},
        "0110D": {'0109D', '0101G', '0209D', '0210D'},
        "0210D": {'0209D', '0301G', '0310D', '0110D', '0101G', '0201G'},
        "0310D": {'0410D', '0210D', '0409D', '0209D', '0301G', '0309D'},
        "0410D": {'0409D', '0301G', '0310D', '0510D', '0401G', '0501G'},
        "0510D": {'0410D', '0509D', '0610D', '0409D', '0609D', '0501G'},
        "0610D": {'0601G', '0701G', '0510D', '0609D', '0710D', '0501G'},
        "0710D": {'0610D', '0809D', '0709D', '0701G', '0810D', '0609D'},
        "0810D": {'0910D', '0901G', '0801G', '0809D', '0701G', '0710D'},
        "0910D": {'0901G', '1009D', '0809D', '0810D', '1010D', '0909D'},
        "1010D": {'0910D', '0901G', '0110E', '1009D', '1001G', '0101H'},
        "0110E": {'0209E', '1009D', '0210E', '0101H', '0109E', '1010D'},
        "0210E": {'0310E', '0209E', '0301H', '0110E', '0201H', '0101H'},
        "0310E": {'0209E', '0309E', '0301H', '0210E', '0410E', '0409E'},
        "0410E": {'0310E', '0510E', '0301H', '0401H', '0501H', '0409E'},
        "0510E": {'0509E', '0410E', '0501H', '0609E', '0610E', '0409E'},
        "0610E": {'0510E', '0601H', '0701H', '0501H', '0609E', '0710E'},
        "0710E": {'0809E', '0709E', '0701H', '0810E', '0609E', '0610E'},
        "0810E": {'0901H', '0809E', '0910E', '0701H', '0801H', '0710E'},
        "0910E": {'0901H', '0809E', '0909E', '1010E', '0810E', '1009E'},
        "1010E": {'0901H', '0110F', '0910E', '1001H', '0101J', '1009E'},
        "0110F": {'0209F', '0210F', '0109F', '1010E', '0101J', '1009E'},
        "0210F": {'0301J', '0209F', '0110F', '0310F', '0101J', '0201J'},
        "0310F": {'0301J', '0209F', '0210F', '0410F', '0409F', '0309F'},
        "0410F": {'0301J', '0510F', '0501J', '0401J', '0310F', '0409F'},
        "0510F": {'0609F', '0509F', '0501J', '0410F', '0610F', '0409F'},
        "0610F": {'0609F', '0510F', '0701J', '0710F', '0501J', '0601J'},
        "0710F": {'0609F', '0809F', '0701J', '0709F', '0610F', '0810F'},
        "0810F": {'0809F', '0701J', '0710F', '0801J', '0901J', '0910F'},
        "0910F": {'0809F', '1010F', '0901J', '0810F', '1009F', '0909F'},
        "1010F": {'0910F', '1001J', '1009F', '0901J'},
        "0110G": {'0209G', '0210G', '0109G'},
        "0210G": {'0209G', '0310G', '0110G'},
        "0310G": {'0410G', '0309G', '0210G', '0409G', '0209G'},
        "0410G": {'0409G', '0310G', '0510G'},
        "0510G": {'0410G', '0610G', '0609G', '0409G', '0509G'},
        "0610G": {'0510G', '0609G', '0710G'},
        "0710G": {'0610G', '0810G', '0809G', '0609G', '0709G'},
        "0810G": {'0809G', '0910G', '0710G'},
        "0910G": {'1010G', '0810G', '0809G', '0909G', '1009G'},
        "1010G": {'1009G', '0910G', '0110H'},
        "0110H": {'0210H', '1009G', '0109H', '0209H', '1010G'},
        "0210H": {'0310H', '0110H', '0209H'},
        "0310H": {'0410H', '0209H', '0309H', '0210H', '0409H'},
        "0410H": {'0510H', '0310H', '0409H'},
        "0510H": {'0410H', '0610H', '0609H', '0509H', '0409H'},
        "0610H": {'0510H', '0710H', '0609H'},
        "0710H": {'0610H', '0609H', '0809H', '0709H', '0810H'},
        "0810H": {'0809H', '0710H', '0910H'},
        "0910H": {'1010H', '1009H', '0809H', '0909H', '0810H'},
        "1010H": {'0910H', '1009H', '0110J'},
        "0110J": {'0210J', '0109J', '0209J', '1009H', '1010H'},
        "0210J": {'0110J', '0310J', '0209J'},
        "0310J": {'0210J', '0209J', '0410J', '0409J', '0309J'},
        "0410J": {'0510J', '0310J', '0409J'},
        "0510J": {'0509J', '0609J', '0410J', '0409J', '0610J'},
        "0610J": {'0710J', '0510J', '0609J'},
        "0710J": {'0609J', '0810J', '0809J', '0709J', '0610J'},
        "0810J": {'0809J', '0910J', '0710J'},
        "0910J": {'0909J', '1009J', '0810J', '0809J', '1010J'},
        "1010J": {'1009J', '0910J'},
    }

    left2neighbors = {
        "0101A": {'0102A', '0201A', 'escape'},
        "0102A": {'0101A', '0201A', '0103A', '0202A'},
        "0103A": {'0203A', '0102A', '0104A', '0202A'},
        "0104A": {'0203A', '0204A', '0103A', '0105A'},
        "0105A": {'0205A', '0204A', '0104A', '0106A'},
        "0106A": {'0105A', '0205A', '0107A', '0206A'},
        "0107A": {'0108A', '0207A', '0106A', '0206A'},
        "0108A": {'0109A', '0208A', '0207A', '0107A'},
        "0109A": {'0108A', '0208A', '0209A', '0110A'},
        "0110A": {'0101D', '0209A', '0109A', '0210A'},
        "0101B": {'0102B', 'escape', '1001A', '0201B'},
        "0102B": {'1002A', '0202B', '1001A', '0101B', '0201B', '0103B'},
        "0103B": {'0102B', '1003A', '0203B', '1002A', '0202B', '0104B'},
        "0104B": {'1003A', '0203B', '1004A', '0204B', '0105B', '0103B'},
        "0105B": {'1004A', '0106B', '1005A', '0204B', '0205B', '0104B'},
        "0106B": {'1006A', '1005A', '0205B', '0105B', '0107B', '0206B'},
        "0107B": {'0106B', '1006A', '0207B', '1007A', '0206B', '0108B'},
        "0108B": {'0208B', '0109B', '0207B', '1007A', '1008A', '0107B'},
        "0109B": {'1009A', '0208B', '0209B', '0110B', '1008A', '0108B'},
        "0110B": {'1009A', '1010A', '0210B', '0109B', '0209B', '0101E'},
        "0101C": {'0102C', 'escape', '1001B', '0201C'},
        "0102C": {'0103C', '1002B', '0201C', '1001B', '0101C', '0202C'},
        "0103C": {'0203C', '1003B', '1002B', '0104C', '0102C', '0202C'},
        "0104C": {'0203C', '0103C', '1003B', '0204C', '1004B', '0105C'},
        "0105C": {'0205C', '1005B', '0204C', '1004B', '0104C', '0106C'},
        "0106C": {'0107C', '0205C', '1005B', '0105C', '0206C', '1006B'},
        "0107C": {'0207C', '0108C', '0206C', '1006B', '1007B', '0106C'},
        "0108C": {'0208C', '0107C', '0207C', '1008B', '0109C', '1007B'},
        "0109C": {'0208C', '1008B', '0108C', '1009B', '0209C', '0110C'},
        "0110C": {'1010B', '0109C', '1009B', '0209C', '0210C', '0101F'},
        "0101D": {'0201D', '0102D', '0110A', '0210A'},
        "0102D": {'0201D', '0101D', '0202D', '0103D'},
        "0103D": {'0203D', '0202D', '0102D', '0104D'},
        "0104D": {'0204D', '0203D', '0105D', '0103D'},
        "0105D": {'0204D', '0205D', '0104D', '0106D'},
        "0106D": {'0206D', '0205D', '0105D', '0107D'},
        "0107D": {'0108D', '0206D', '0207D', '0106D'},
        "0108D": {'0208D', '0109D', '0107D', '0207D'},
        "0109D": {'0108D', '0208D', '0209D', '0110D'},
        "0110D": {'0210D', '0109D', '0209D', '0101G'},
        "0101E": {'1010A', '0110B', '0102E', '0210B', '1001D', '0201E'},
        "0102E": {'0201E', '0103E', '1001D', '0202E', '1002D', '0101E'},
        "0103E": {'1003D', '0203E', '0104E', '0102E', '0202E', '1002D'},
        "0104E": {'0103E', '1003D', '0203E', '1004D', '0204E', '0105E'},
        "0105E": {'0106E', '1005D', '1004D', '0205E', '0104E', '0204E'},
        "0106E": {'0206E', '1006D', '1005D', '0107E', '0205E', '0105E'},
        "0107E": {'0206E', '1006D', '0106E', '0207E', '0108E', '1007D'},
        "0108E": {'1008D', '0207E', '0107E', '0109E', '1007D', '0208E'},
        "0109E": {'1008D', '0110E', '0108E', '0209E', '1009D', '0208E'},
        "0110E": {'0101H', '0209E', '1010D', '0109E', '0210E', '1009D'},
        "0101F": {'0102F', '1010B', '0210C', '0110C', '0201F', '1001E'},
        "0102F": {'0201F', '1001E', '1002E', '0103F', '0101F', '0202F'},
        "0103F": {'0102F', '1003E', '1002E', '0104F', '0203F', '0202F'},
        "0104F": {'1003E', '1004E', '0103F', '0105F', '0203F', '0204F'},
        "0105F": {'0205F', '0106F', '1004E', '0204F', '0104F', '1005E'},
        "0106F": {'0205F', '1006E', '0107F', '0105F', '0206F', '1005E'},
        "0107F": {'1006E', '0207F', '1007E', '0206F', '0108F', '0106F'},
        "0108F": {'0107F', '0208F', '0109F', '0207F', '1007E', '1008E'},
        "0109F": {'0208F', '0209F', '1009E', '1008E', '0108F', '0110F'},
        "0110F": {'1010E', '0101J', '0109F', '0209F', '0210F', '1009E'},
        "0101G": {'0201G', '0210D', '0102G', '0110D'},
        "0102G": {'0201G', '0202G', '0101G', '0103G'},
        "0103G": {'0203G', '0102G', '0202G', '0104G'},
        "0104G": {'0203G', '0204G', '0105G', '0103G'},
        "0105G": {'0204G', '0205G', '0104G', '0106G'},
        "0106G": {'0206G', '0107G', '0205G', '0105G'},
        "0107G": {'0206G', '0106G', '0207G', '0108G'},
        "0108G": {'0208G', '0107G', '0207G', '0109G'},
        "0109G": {'0208G', '0108G', '0209G', '0110G'},
        "0110G": {'0210G', '0209G', '0109G'},
        "0101H": {'0210E', '0102H', '0110E', '1010D', '0201H', '1001G'},
        "0102H": {'0202H', '0101H', '0103H', '1002G', '0201H', '1001G'},
        "0103H": {'0202H', '1002G', '0104H', '0203H', '1003G', '0102H'},
        "0104H": {'0103H', '0203H', '1003G', '1004G', '0105H', '0204H'},
        "0105H": {'0205H', '1005G', '0106H', '0104H', '1004G', '0204H'},
        "0106H": {'0205H', '0206H', '0107H', '1005G', '0105H', '1006G'},
        "0107H": {'0206H', '0106H', '1007G', '0108H', '0207H', '1006G'},
        "0108H": {'0208H', '0107H', '1008G', '1007G', '0207H', '0109H'},
        "0109H": {'0208H', '1009G', '0110H', '1008G', '0108H', '0209H'},
        "0110H": {'1009G', '0210H', '0109H', '0209H', '1010G'},
        "0101J": {'0210F', '0110F', '1010E', '0102J', '1001H', '0201J'},
        "0102J": {'0101J', '0201J', '0103J', '1002H', '1001H', '0202J'},
        "0103J": {'0102J', '0104J', '1003H', '1002H', '0203J', '0202J'},
        "0104J": {'1004H', '0103J', '1003H', '0105J', '0204J', '0203J'},
        "0105J": {'1004H', '0205J', '0104J', '1005H', '0204J', '0106J'},
        "0106J": {'0205J', '1005H', '0105J', '1006H', '0206J', '0107J'},
        "0107J": {'1007H', '0108J', '1006H', '0207J', '0206J', '0106J'},
        "0108J": {'1008H', '1007H', '0109J', '0208J', '0207J', '0107J'},
        "0109J": {'1008H', '0209J', '1009H', '0110J', '0108J', '0208J'},
        "0110J": {'1009H', '0209J', '0109J', '0210J', '1010H'}
    }

    right2neighbors = {
        "1001A": {'0901A', '0902A', '0102B', '1002A', '0101B'},
        "1002A": {'1003A', '1001A', '0902A', '0903A', '0103B', '0102B'},
        "1003A": {'1004A', '0904A', '1002A', '0903A', '0103B', '0104B'},
        "1004A": {'1003A', '0105B', '1005A', '0904A', '0905A', '0104B'},
        "1005A": {'0906A', '1006A', '1004A', '0106B', '0905A', '0105B'},
        "1006A": {'0906A', '1005A', '0907A', '0106B', '0107B', '1007A'},
        "1007A": {'0908A', '1006A', '0907A', '0108B', '0107B', '1008A'},
        "1008A": {'0908A', '0109B', '1009A', '0108B', '0909A', '1007A'},
        "1009A": {'0910A', '0109B', '1010A', '0909A', '0110B', '1008A'},
        "1010A": {'0910A', '1009A', '0101E', '0901D', '0110B', '1001D'},
        "1001B": {'0902B', '0901B', '1002B', '0102C', '0101C'},
        "1002B": {'0103C', '1003B', '0902B', '0903B', '0102C', '1001B'},
        "1003B": {'0103C', '1004B', '0904B', '0903B', '0104C', '1002B'},
        "1004B": {'0904B', '1005B', '1003B', '0104C', '0905B', '0105C'},
        "1005B": {'1004B', '1006B', '0106C', '0906B', '0905B', '0105C'},
        "1006B": {'0107C', '1007B', '1005B', '0907B', '0106C', '0906B'},
        "1007B": {'0107C', '1006B', '0908B', '1008B', '0907B', '0108C'},
        "1008B": {'0909B', '1007B', '0908B', '1009B', '0109C', '0108C'},
        "1009B": {'0910B', '0909B', '0110C', '1008B', '0109C', '1010B'},
        "1010B": {'0101F', '0910B', '0901E', '0110C', '1009B', '1001E'},
        "1001C": {'1002C', '0901C', '0902C'},
        "1002C": {'0903C', '1003C', '1001C', '0902C'},
        "1003C": {'1002C', '0903C', '1004C', '0904C'},
        "1004C": {'1005C', '0904C', '0905C', '1003C'},
        "1005C": {'1004C', '1006C', '0905C', '0906C'},
        "1006C": {'1007C', '1005C', '0907C', '0906C'},
        "1007C": {'0908C', '0907C', '1006C', '1008C'},
        "1008C": {'0909C', '1007C', '0908C', '1009C'},
        "1009C": {'0909C', '1010C', '0910C', '1008C'},
        "1010C": {'0901F', '1001F', '0910C', '1009C'},
        "1001D": {'1002D', '0102E', '0902D', '1010A', '0901D', '0101E'},
        "1002D": {'1003D', '0903D', '0103E', '0902D', '0102E', '1001D'},
        "1003D": {'0903D', '0103E', '1002D', '1004D', '0904D', '0104E'},
        "1004D": {'1003D', '1005D', '0905D', '0105E', '0904D', '0104E'},
        "1005D": {'0905D', '1004D', '0105E', '0106E', '1006D', '0906D'},
        "1006D": {'1005D', '0907D', '1007D', '0106E', '0107E', '0906D'},
        "1007D": {'0908D', '0907D', '1008D', '1006D', '0107E', '0108E'},
        "1008D": {'0908D', '0109E', '1007D', '0108E', '1009D', '0909D'},
        "1009D": {'0110E', '0109E', '1010D', '1008D', '0910D', '0909D'},
        "1010D": {'1001G', '0110E', '0901G', '0101H', '0910D', '1009D'},
        "1001E": {'0902E', '0901E', '1002E', '0102F', '1010B', '0101F'},
        "1002E": {'0903E', '0902E', '0103F', '1003E', '1001E', '0102F'},
        "1003E": {'0903E', '0904E', '0104F', '0103F', '1004E', '1002E'},
        "1004E": {'0904E', '0104F', '0105F', '1003E', '0905E', '1005E'},
        "1005E": {'0105F', '0106F', '0906E', '0905E', '1004E', '1006E'},
        "1006E": {'0106F', '1005E', '0107F', '0906E', '1007E', '0907E'},
        "1007E": {'0107F', '0108F', '0907E', '1006E', '1008E', '0908E'},
        "1008E": {'0909E', '0109F', '0108F', '1007E', '1009E', '0908E'},
        "1009E": {'0909E', '0109F', '1010E', '0910E', '0110F', '1008E'},
        "1010E": {'0910E', '1001H', '0101J', '0110F', '0901H', '1009E'},
        "1001F": {'1002F', '0901F', '1010C', '0902F'},
        "1002F": {'1003F', '1001F', '0903F', '0902F'},
        "1003F": {'1002F', '0903F', '0904F', '1004F'},
        "1004F": {'1003F', '0905F', '0904F', '1005F'},
        "1005F": {'0905F', '1006F', '0906F', '1004F'},
        "1006F": {'1005F', '0907F', '0906F', '1007F'},
        "1007F": {'0907F', '1006F', '1008F', '0908F'},
        "1008F": {'1009F', '0908F', '0909F', '1007F'},
        "1009F": {'1010F', '0910F', '1008F', '0909F'},
        "1010F": {'1009F', '0901J', '0910F', '1001J'},
        "1001G": {'0102H', '0901G', '1010D', '1002G', '0902G', '0101H'},
        "1002G": {'1001G', '0102H', '1003G', '0903G', '0103H', '0902G'},
        "1003G": {'0904G', '1004G', '0903G', '1002G', '0103H', '0104H'},
        "1004G": {'0904G', '1003G', '0105H', '1005G', '0905G', '0104H'},
        "1005G": {'1004G', '0105H', '0905G', '1006G', '0906G', '0106H'},
        "1006G": {'0907G', '1005G', '1007G', '0107H', '0906G', '0106H'},
        "1007G": {'0908G', '0907G', '0108H', '1008G', '1006G', '0107H'},
        "1008G": {'1009G', '0908G', '0108H', '0909G', '1007G', '0109H'},
        "1009G": {'0110H', '1010G', '0910G', '1008G', '0909G', '0109H'},
        "1010G": {'1009G', '0910G', '0110H'},
        "1001H": {'1010E', '0902H', '0901H', '0102J', '1002H', '0101J'},
        "1002H": {'1003H', '1001H', '0103J', '0902H', '0102J', '0903H'},
        "1003H": {'0903H', '0103J', '0104J', '0904H', '1004H', '1002H'},
        "1004H": {'1003H', '0104J', '1005H', '0905H', '0105J', '0904H'},
        "1005H": {'0906H', '0106J', '0905H', '0105J', '1006H', '1004H'},
        "1006H": {'0906H', '1005H', '0106J', '0107J', '1007H', '0907H'},
        "1007H": {'0108J', '0908H', '0107J', '1008H', '1006H', '0907H'},
        "1008H": {'0109J', '0108J', '0908H', '1009H', '0909H', '1007H'},
        "1009H": {'1010H', '0109J', '0910H', '0110J', '1008H', '0909H'},
        "1010H": {'1009H', '0910H', '0110J'},
        "1001J": {'1010F', '0901J', '1002J', '0902J'},
        "1002J": {'0903J', '1001J', '0902J', '1003J'},
        "1003J": {'0903J', '0904J', '1004J', '1002J'},
        "1004J": {'0904J', '1005J', '0905J', '1003J'},
        "1005J": {'1006J', '1004J', '0906J', '0905J'},
        "1006J": {'1005J', '0907J', '1007J', '0906J'},
        "1007J": {'1006J', '1008J', '0907J', '0908J'},
        "1008J": {'1009J', '1007J', '0908J', '0909J'},
        "1009J": {'1008J', '1010J', '0909J', '0910J'},
        "1010J": {'1009J', '0910J'}
    }

    test_dict = {'Top': top2neighbors, 'Bottom': bottom2neighbors, 'Left': left2neighbors, 'Right': right2neighbors}

    return test_dict
