from simulator.novelty_functions import *
from simulator.weapon import Weapon
from simulator.player import Player
from simulator.action_choices import *
import simulator.action_choices as action_choices
import copy
import sys

"""
The novelty methods in here should be called after an initial game board has been set up, but before simulate has
been called within gameplay. It is unsafe to introduce novelty in the middle of a 'game'. The novelties should
only operate at the tournament level and be introduced prior to game instance simulation.
"""


class Novelty(object):
    def __init__(self):
        pass


class AttributeNovelty(Novelty):
    def __init__(self):
        super().__init__()


class ClassNovelty(Novelty):
    def __init__(self):
        super().__init__()


class ActionNovelty(Novelty):
    def __init__(self):
        super().__init__()


class WeaponAttributeNovelty(AttributeNovelty):
    def __init__(self):
        super().__init__()

    def customize_weapon_bay_size(self, current_gameboard, new_size):
        """
        weapon_bay_size set to 24 in default which could also be increased or decreased
        :param current_gameboard:
        :param new_size: int size of new weapon_bay
        :return:
        """
        current_gameboard['weapon_bay_size'] = new_size

    # This one current not working, since inject this novelty before initialize weapons
    def customize_weapon_bay_slot(self, current_gameboard, weapon_class, new_slot):
        """
        Change slot of specific weapon, example: 1 for sonobuoy and 2 for torpedo as default
        :param current_gameboard:
        :param weapon_class: String type of name of weapon class
        :param new_slot: new slot size value
        :return:
        """
        for name, weapon in current_gameboard['weapons_inventory'].items():
            if weapon.weapon_class == weapon_class:
                weapon.weapons_bay_slot = new_slot

    def customize_torpedo_speed(self, current_gameboard, turn, new_speed):
        """
        Change speed of torpedo either first or second turn to the new speed
        :param current_gameboard:
        :param turn: first_turn or second_turn in String type
        :param new_speed: int number of new speed for torpedo
        :return:
        """
        current_gameboard['torpedo_speed'][turn] = new_speed

    def customize_torpedo_detection_range(self, current_gameboard, range_num):
        """
        :param current_gameboard:
        :param range_num:
        :return:
        """
        current_gameboard['torpedo_detection_range'] = range_num

    def customize_torpedo_listening_range(self, current_gameboard, range_num):
        """
        :param current_gameboard:
        :param range_num:
        :return:
        """
        current_gameboard['torpedo_listening_range'] = range_num

    def weapon_initialize_two_layer_attributes(self, current_gameboard):
        """
        Create new attribute to present two layer property, initialize attributes of weapon to Shallow and could
        also exchange between Shallow and Deep
        :param current_gameboard:
        :param attributes: dict("two_layer": dict("Shallow": ["S", "D"]))
        :return:
        """
        for name, weapon in current_gameboard['weapons_inventory'].items():
            # if weapon.weapon_class == 'sonobuoy':
            weapon.attributes = {'two_layer': 'Shallow'}


class PlayerAttributeNovelty(AttributeNovelty):
    def __int__(self):
        super().__init__()

    def panther_initialize_two_layer_attributes(self, current_gameboard):
        """
        Add additional attributes for panther player, could also modify this func in order to add attributes for the
        pelican player in the future
        :param current_gameboard:
        :param attributes: dict of additional attributes
        :return:
        """
        for player in current_gameboard['players']:
            if player.player_class == 'Panther':
                player.additional_attributes = {'two_layer': 'Shallow'}


class ShipAttributeNovelty(AttributeNovelty):
    def __init__(self):
        super().__init__()

    def customize_plark_detect_range(self, current_gameboard, stop_range, slow_range, fast_range):
        """
        Change maximum range of detecting sonobuoys and torpedos for plark depending on different types of speed
        :param current_gameboard:
        :param stop_range: range in stop status
        :param slow_range: range in slow status
        :param fast_range: range in fast status
        :return:
        """
        detect_dict = {
            'stopped': stop_range,
            'slow': slow_range,
            'fast': fast_range
        }
        current_gameboard['detection_range'] = detect_dict


class WeaponActionNovelty(ActionNovelty):
    def __init__(self):
        super().__init__()

    def make_torpedo_re_attack(self, current_gameboard, alternate_func):
        """
        If it's first turn and missing target for torpedo, it should not be removed but instead set to second turn
        :param current_gameboard:
        :param alternate_func: new function for torpedo to behave
        :return:
        """
        action_choices._remove_torpedo_after_die_roll = getattr(sys.modules[__name__], alternate_func)

    def weapon_two_layer_decision(self, current_gameboard, alternate_func):
        """

        :param current_gameboard:
        :param alternate_func:
        :return:
        """
        action_choices._drop_sonobuoy = getattr(sys.modules[__name__], alternate_func)

    def sonobuoy_detect_range_behavior(self, current_gameboard, alternate_func):
        """

        :param current_gameboard:
        :param alternate_func:
        :return:
        """
        action_choices._sonobuoy_setting_helper = getattr(sys.modules[__name__], alternate_func)

    def torpedo_detect_range_behavior(self, current_gameboard, alternate_func):
        """

        :param current_gameboard:
        :param alternate_func:
        :return:
        """
        action_choices._torpedo_detect_plark_helper = getattr(sys.modules[__name__], alternate_func)


class PlayerActionNovelty(ActionNovelty):
    def __init__(self):
        super().__init__()

    def player_two_layer_decision(self, current_gameboard, alternate_func):
        """
        Panther could change its depth to either Shallow or Deep in order to avoid detect or attack from sonubuoys
        and torpedos
        :param current_gameboard:
        :param alternate_func:
        :return:
        """
        action_choices._move_panther_helper = getattr(sys.modules[__name__], alternate_func)

