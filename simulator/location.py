import networkx as nx

class Location(object):
    def __init__(self,location_name,submap,state='undisturbed'):
        self.special_position_flags = set() #will allow us to determine if the location is in a corner, border etc.
        self.location_name = location_name # a string; contains the submap also e.g. '0101A'
        self.submap = submap # a string in ['A','B','C','D','E','F','G','H','J'], None for escape
        self.neighbors = set() # the set of neighbors of the token; only escape has no neighbors
        self.num_neighbors = -1
        self.disturbed_water = False
        self.underwater_explosion = False

    def update_neighbors(self, neighbors):
        self.neighbors = neighbors
        self.num_neighbors = len(self.neighbors)

    def serialize_neighbors(self):
        ans = set()
        for n in self.neighbors:
            ans.add(n.location_name)
        return ans

    def update_special_position_flags(self, special_position_flags):
        self.special_position_flags = special_position_flags # subset of {top_left_corner, top_right_corner, left_edge,
                                # right_edge, top_edge, bottom_edge, bottom_left_corner, bottom_right_corner, panther_zone}
                                # in the current game, there's no token with top right corner

    def calculate_distance(self, current_gameboard, location): # to come
        G = current_gameboard['game_graph']
        target = location.location_name
        source = self.location_name
        return len(list(nx.shortest_path(G, source=source, target=target)))-1

    def _print_location_data(self):
        print('location name: ',self.location_name)
        print('location submap: ', self.submap)
        print('num neighbors: ', str(self.num_neighbors))
        print('location special position flags: ', ','.join(list(self.special_position_flags)))
        print('location neighbors: ',','.join([n.location_name for n in self.neighbors]))

    def locate_nearest_disturbed_water(self, current_gameboard):
        print('locating nearest disturbed water for ',self.location_name)
        min_dist = -1
        ans = None
        for location_name, location in current_gameboard['location_map'].items():
            if location.disturbed_water:
                m = self.calculate_distance(current_gameboard, location)
                if min_dist == -1 or m < min_dist:
                    min_dist = m
                    ans = location
        if not ans:
            print('disturbed water does not exist, returning None')
        else:
            print('disturbed water found at location ',ans.location_name,' at distance ',str(min_dist))
        return ans

    def locate_nearest_underwater_explosion(self, current_gameboard):
        print('locating nearest underwater explosion for ', self.location_name)
        min_dist = -1
        ans = None
        for location_name, location in current_gameboard['location_map'].items():
            if location.underwater_explosion:
                m = self.calculate_distance(current_gameboard, location)
                if min_dist == -1 or m < min_dist:
                    min_dist = m
                    ans = location
        if not ans:
            print('underwater explosion does not exist, returning None')
        else:
            print('underwater explosion found at location ',ans.location_name,' at distance ',str(min_dist))
        return ans

    def locate_dropped_torpedos_within_range(self, current_gameboard, range_threshold):
        print('locating minimal-distance dropped torpedoes within range ',str(range_threshold),' of location ', self.location_name)
        print('note that torpedoes on this location will not be included in answer-set. Torpedoes not minimally distant, but within range, will also not be included.')

        # self location is not included or checked
        torpedos = set()
        torpedo_dis = None
        for weapon_name, weapon in current_gameboard['weapons_inventory'].items():
            if weapon.weapon_class != 'torpedo':
                continue
            if weapon.state == 'undropped' or weapon.state == 'removed':
                continue
            if weapon.location == self:
                continue
            m = self.calculate_distance(current_gameboard, weapon.location)
            if m <= range_threshold:
                if torpedo_dis is None or m == torpedo_dis:
                    torpedo_dis = m
                    print('adding dropped torpedo ', weapon.weapon_name, ' at distance ', str(m), ' to torpedos set.')
                    torpedos.add(weapon)

                elif m < torpedo_dis:
                    torpedo_dis = m
                    print('resetting torpedo set since torpedoes found at closer distance...')
                    torpedos = set() # re-set torpedos since there's a closer one in range
                    print('adding dropped torpedo ', weapon.weapon_name, ' at distance ', str(m), ' to torpedos set.')
                    torpedos.add(weapon)

        if not torpedo_dis:
            print('there are no dropped torpedoes within range.')

        return (torpedo_dis, torpedos) # iff torpedo_dis is non_none then torpedos will be non-empty.


    def compute_shortest_path(self, current_gameboard, target_location):
        G = current_gameboard['game_graph']
        return list(nx.shortest_path(G, source=self.location_name, target=target_location.location_name))

    def triggers_torpedo_sensor(self, weapon, current_gameboard):
        print('has torpedo sensor been triggered for location ',self.location_name,'?')
        print('torpedo sensor will be triggered if there is plark on this location or there is a torpedo other than ',weapon.weapon_name,' on this location.')
        # returns true if the plark is in this position or if there's a DIFFERENT dropped torpedo in this position
        plark = None
        for p in current_gameboard['players']:
            if p.player_class == 'Panther':
                plark = p
                break

        if plark.current_position == self:
            print('plark is in position ',self.location_name,'. Returning True...')
            return True

        for weapon_name, w in current_gameboard['weapons_inventory'].items():
            if w.weapon_class != 'torpedo' or (w.state == 'undropped' or w.state == 'removed') or w==weapon:
                continue
            elif w.location == self:
                print('we found a torpedo here: ',str(weapon_name))
                print('Returning True...')
                return True

        print('torpedo sensor was not triggered. Returning False...')
        return False





