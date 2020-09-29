

def flip_torpedo(torpedo):
    """

    :return: None
    """
    print('In utility_actions.flip_torpedo...')
    if torpedo.state == 'first_turn':
        torpedo.state = 'second_turn'
        print('flipping state for torpedo ', torpedo.weapon_name,' from first turn to second turn')
    else:
        print(torpedo.weapon_name, ' has been removed from the board.')
        torpedo.state = 'removed'
        torpedo.location = None



def is_plark_sunk(current_gameboard):
    print('Has the plark been sunk?')
    for p in current_gameboard['players']:
        if p.player_class == 'Pelican':
            continue
        if p.player_class == 'Panther' and p.damage_status == 'sunk':
            print(p.player_name, ' is sunk. Returning True')
            return True
        else:
            print(p.player_name, ' is not sunk. Returning False')
            return False

def check_for_winner(current_gameboard):
    print('checking for winner...')
    for p in current_gameboard['players']:
        if p.player_class == 'Panther' and p.damage_status == 'undamaged':
            print(p.player_name,' is undamaged. Returning ',p.player_name)
            return p
        elif p.damage_status == 'sunk':
            print(p.player_name, ' has been sunk')
            for m in current_gameboard['players']:
                if m.player_class == 'Pelican':
                    print(m.player_name, ' is the winner since plark is sunk')
                    return m
    print('there is no winner. Returnign None...')
    return None


def has_plark_escaped(current_gameboard):
    print('Has the plark escaped?')
    for p in current_gameboard['players']:
        if p.player_class == 'Panther':
            if p.current_position.location_name == 'escape':
                print('Yes. Returning True...')
                return True
            else:
                print('No. Returning False...')
                return False


def check_for_winchester(current_gameboard):
    print('checking for winchester...')
    for p in current_gameboard['players']:
        if p.player_class == 'Pelican':

            for weapon_name, weapon in current_gameboard['weapons_inventory'].items():
                if weapon.weapon_class == 'torpedo' and \
                        (weapon.state == 'undropped' or weapon.state == 'first_turn' or weapon.state == 'second_turn'):
                    print(f'Some torpedos are undropped or still running on the board')
                    return False

            if not p.weapons_bay['torpedo']:
                print(p.player_name,' does not have any torpedoes. Returning True...')
                return True
            else:
                print(p.player_name, ' still has torpedoes. Returning False...')
                return False