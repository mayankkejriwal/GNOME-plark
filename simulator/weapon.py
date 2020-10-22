class Weapon(object):
    def __init__(self, weapon_name, weapon_class, weapons_bay_slot,location, player):
        self.weapon_name = weapon_name
        self.weapon_class = weapon_class
        self.weapons_bay_slot = weapons_bay_slot
        self.location = location # this is a location instance
        self.player = player # note that even after the weapon is dropped, the player is still maintained so we
        self.attributes = None  # either None or dict, if dict(key:name_attribute, value: dict(keys:current_value, list possible values))
        #can track where the weapon came from.


class Sonobuoy(Weapon):
    def __init__(self, weapon_name, state='undropped', weapons_bay_slot=1, location=None, player=None):
        super().__init__(weapon_name, 'sonobuoy',weapons_bay_slot, location, player) # default value is 1
        self.state = state # allowable states are undropped, cold, hot, removed.


class Torpedo(Weapon):
    def __init__(self, weapon_name, state='undropped', weapons_bay_slot=2,location=None, player=None):
        super().__init__(weapon_name, 'torpedo',weapons_bay_slot, location, player) # default value is 2
        self.state=state # allowable states are undropped, first_turn,second_turn,removed