import copy

from simulator import novelty_generator
from simulator import novelty_functions


def weapon_bay_size_change(current_gameboard, bay_size=50):
    """
    Option Rule for 7.1 and 7.2 to reduce or increase weapon bay size to either 28 or 20
    Actually we could change this size to any thing we want if make sense
    :param current_gameboard:
    :param bay_size: new weapon bay size to hold weapons
    :return:
    """
    WeaponAttributeNovelty = novelty_generator.WeaponAttributeNovelty()
    WeaponAttributeNovelty.customize_weapon_bay_size(current_gameboard, bay_size)


def torpedo_re_attach(current_gameboard, alternate_func='torpedo_attack_again_if_miss'):
    """
    Make torpedo have ability to re-attach plark if missing in the first turn
    :param current_gameboard:
    :param alternate_func: new method of torpedo to act
    :return:
    """
    WeaponActionNovelty = novelty_generator.WeaponActionNovelty()
    WeaponActionNovelty.make_torpedo_re_attack(current_gameboard, alternate_func=alternate_func)


def two_layer_property(current_gameboard,
                       alternate_func1='drop_sonobuoy_in_two_layer',
                       alternate_func2='panther_decision_in_two_layer',
                       alternate_func3='sonobuoy_consider_two_layer',
                       alternate_func4='torpedo_detect_plark_with_layer'):
    """
    The game board at this time should have two layer: Shallow and Deep.
    If Popcorn, the detection range of sonobuoys and torpedos should both reduce by 2 if panther and weapons are in
    different layers
    :param current_gameboard: dict of game board
    :param alternate_func1: new func for sonobuoy to change depth when drop
    :param alternate_func2: new func for panther to change depth after each move
    :param alternate_func3:
    :param alternate_func4:
    :return:
    """

    # Add two layer property as attribute into both sonubuoy and panther player
    WeaponAttributeNovelty = novelty_generator.WeaponAttributeNovelty()
    PlayerAttributeNovelty = novelty_generator.PlayerAttributeNovelty()

    attributes = {
        'two_layer': ['Shallow', 'Deep']
    }
    current_gameboard['new_attributes'] = copy.deepcopy(attributes)

    # default setting is 'Shallow'
    WeaponAttributeNovelty.weapon_initialize_two_layer_attributes(current_gameboard)
    PlayerAttributeNovelty.panther_initialize_two_layer_attributes(current_gameboard)

    # Modify func in order for panther and sonobuoy could work property with two layer property
    WeaponActionNovelty = novelty_generator.WeaponActionNovelty()
    PlayerActionNovelty = novelty_generator.PlayerActionNovelty()
    WeaponActionNovelty.weapon_two_layer_decision(current_gameboard, alternate_func=alternate_func1)
    PlayerActionNovelty.player_two_layer_decision(current_gameboard, alternate_func=alternate_func2)

    WeaponActionNovelty.sonobuoy_detect_range_behavior(current_gameboard, alternate_func=alternate_func3)
    WeaponActionNovelty.torpedo_detect_range_behavior(current_gameboard, alternate_func=alternate_func4)


def active_torpedo(current_gameboard, speed_dict={'first_turn':5, 'second_turn':3}):
    """
    Active torpedo so that torpedo could attach panther with 3 hexes always
    :param current_gameboard: dict of current game board
    :param speed_dict: new speed dict including first turn and second turn
    :return:
    """
    WeaponAttributeNovelty = novelty_generator.WeaponAttributeNovelty()
    for key, value in speed_dict.items():
        WeaponAttributeNovelty.customize_torpedo_speed(current_gameboard, key, value)
