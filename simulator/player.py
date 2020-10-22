
from simulator.action_choices import *


class Player(object):
    def __init__(self,player_name,agent, player_class):
        """
        An object representing a unique player in the game.

        """
        self.player_name = player_name
        self.agent=agent # the agent assigned to this player.

        self.player_class = player_class # should be either 'Panther' or 'Pelican'.

        self.current_position = None # this is a location instance once initialized
        self.weapons_bay = None # a dict with keys 'sonobuoy' and 'torpedo' referring to sets with weapon instances
        self.MAD = None

        if self.player_class == 'Pelican':
            self.MAD = False

        self.status = 'waiting'
        self.damage_status = None # only applies to plark. should be one of 'sunk', 'damaged' or 'undamaged'

        self.path_history = list() # this is a list of lists. It traces the player's path throughout the board. It applies to both pelican and panther.
        self.additional_attributes = None # these are for things such as recording whether a sub is deep or shallow etc. It does not apply in the default game.
        self.additional_attributes_history = list()

    def change_decision_agent(self, agent):
        print('changing decision agent for ',self.player_name)
        self.agent = agent

    def manipulate_MAD(self, new_MAD):

        if self.MAD is None:
            print('Error! ' + self.player_name + ' has no MAD to manipulate')
            return
        print('setting new MAD for ',self.player_name,' whose current MAD status is ',self.MAD)
        self.MAD = new_MAD
        print(self.player_name,' now has MAD status ',self.MAD)

    def eject_sonobuoy(self, ID=None): # if you're a panther, the eject functions should not be used.
        if not self.weapons_bay['sonobuoy']:
            print(self.player_name,' is trying to eject a sonobuoy but has no sonobuoys remaining...')
            return None
        if ID:
            for s in self.weapons_bay['sonobuoy']:
                if s.weapon_name == ID:
                    print('ejecting sonobuoy with ID ',ID,' for player ',self.player_name)
                    self.weapons_bay['sonobuoy'].remove(s)
                    return s
            print('there is no sonobuoy with ID: ', ID, ' in the weapons bay of ',self.player_name)
            return None

        elif ID is None:
            print('ejecting random sonobuoy from weapons bay of ',self.player_name)
            rand_sono = list(self.weapons_bay['sonobuoy'])[0]
            self.weapons_bay['sonobuoy'].remove(rand_sono)
            print('ejected sonobuoy ', rand_sono.weapon_name)
            return rand_sono

    def eject_torpedo(self, ID=None):
        if not self.weapons_bay['torpedo']:
            print(self.player_name, ' is trying to eject a torpedo but has no torpedoes remaining...')
            return None
        if ID:
            for s in self.weapons_bay['torpedo']:
                if s.weapon_name == ID:
                    print('ejecting torpedo with ID ', ID, ' for player ', self.player_name)
                    self.weapons_bay['torpedo'].remove(s)
                    return s
                print('there is no torpedo with ID: ', ID, ' in the weapons bay of ', self.player_name)
            return None

        elif ID is None:
            print('ejecting random torpedo from weapons bay of ', self.player_name)
            rand_torp = list(self.weapons_bay['torpedo'])[0]
            self.weapons_bay['torpedo'].remove(rand_torp)
            print('ejected torpedo ',rand_torp.weapon_name)
            return rand_torp

    def compute_allowable_pelican_phase_actions(self, current_gameboard):
        print('computing allowable pelican phase actions for ' + self.player_name)
        allowable_actions = set()
        allowable_actions.add(null_action)
        allowable_actions.add(move_pelican_drop_weapons)

        return allowable_actions

    def compute_allowable_madman_phase_actions(self, current_gameboard):
        print('computing allowable madman phase actions for ' + self.player_name)
        allowable_actions = set()
        allowable_actions.add(null_action)
        allowable_actions.add(flip_pelican_counter)

        return allowable_actions

    def compute_allowable_maypole_phase_actions(self, current_gameboard):
        print('computing allowable maypole phase actions for ' + self.player_name)
        allowable_actions = set()
        allowable_actions.add(null_action)
        allowable_actions.add(update_sonobuoys)

        return allowable_actions

    def compute_allowable_panther_phase_actions(self, current_gameboard):
        print('computing allowable panther phase actions for ' + self.player_name)
        allowable_actions = set()
        allowable_actions.add(null_action)
        allowable_actions.add(move_panther)

        return allowable_actions

    def compute_allowable_bloodhound_phase_actions(self, current_gameboard):
        print('computing allowable bloodhound phase actions for ' + self.player_name)
        allowable_actions = set()
        allowable_actions.add(null_action)
        allowable_actions.add(move_update_torpedoes)

        return allowable_actions

    def make_pelican_phase_moves(self, current_gameboard):
        """
        :param current_gameboard: A dict. The global data structure representing the current game board.
        :return: An integer
        """
        print('We are in the pelican phase for '+self.player_name)
        allowable_actions = self.compute_allowable_pelican_phase_actions(current_gameboard)

        code = 0
        action_to_execute, parameters = self.agent.make_pelican_phase_move(self, current_gameboard, allowable_actions, code)
        t = (action_to_execute, parameters)
        # add to game history
        current_gameboard['history']['function'].append(self.agent.make_pelican_phase_move)
        params = dict()
        params['player'] = self
        params['current_gameboard'] = current_gameboard
        params['allowable_moves'] = allowable_actions
        params['code'] = code
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(t)

        if action_to_execute == null_action:
            return self._execute_action(action_to_execute, parameters, current_gameboard)

        return self._execute_action(action_to_execute, parameters, current_gameboard)

    def make_madman_phase_moves(self, current_gameboard):
        """
        :param current_gameboard: A dict. The global data structure representing the current game board.
        :return: An integer
        """
        print('We are in the madman phase for '+self.player_name)
        allowable_actions = self.compute_allowable_madman_phase_actions(current_gameboard)
        # if 1 or 2, add sonobuoy in allowable moves

        code = 0
        action_to_execute, parameters = self.agent.make_madman_phase_move(self, current_gameboard, allowable_actions, code)
        t = (action_to_execute, parameters)
        # add to game history
        current_gameboard['history']['function'].append(self.agent.make_madman_phase_move)
        params = dict()
        params['player'] = self
        params['current_gameboard'] = current_gameboard
        params['allowable_moves'] = allowable_actions
        params['code'] = code
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(t)

        if action_to_execute == null_action:
            return self._execute_action(action_to_execute, parameters, current_gameboard)

        return self._execute_action(action_to_execute, parameters, current_gameboard)

    def make_maypole_phase_moves(self, current_gameboard):
        """
        :param current_gameboard: A dict. The global data structure representing the current game board.
        :return: An integer
        """
        print('We are in the maypole phase for '+self.player_name)
        allowable_actions = self.compute_allowable_maypole_phase_actions(current_gameboard)

        code = 0
        action_to_execute, parameters = self.agent.make_maypole_phase_move(self, current_gameboard, allowable_actions, code)
        t = (action_to_execute, parameters)
        # add to game history
        current_gameboard['history']['function'].append(self.agent.make_maypole_phase_move)
        params = dict()
        params['player'] = self
        params['current_gameboard'] = current_gameboard
        params['allowable_moves'] = allowable_actions
        params['code'] = code
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(t)

        if action_to_execute == null_action:
            return self._execute_action(action_to_execute, parameters, current_gameboard)

        return self._execute_action(action_to_execute, parameters, current_gameboard)

    def make_panther_phase_moves(self, current_gameboard):
        """
        :param current_gameboard: A dict. The global data structure representing the current game board.
        :return: An integer
        """
        print('We are in the panther phase for '+self.player_name)
        allowable_actions = self.compute_allowable_panther_phase_actions(current_gameboard)

        code = 0
        action_to_execute, parameters = self.agent.make_panther_phase_move(self, current_gameboard, allowable_actions, code)
        t = (action_to_execute, parameters)
        # add to game history
        current_gameboard['history']['function'].append(self.agent.make_panther_phase_move)
        params = dict()
        params['player'] = self
        params['current_gameboard'] = current_gameboard
        params['allowable_moves'] = allowable_actions
        params['code'] = code
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(t)

        if action_to_execute == null_action:
            return self._execute_action(action_to_execute, parameters, current_gameboard)

        return self._execute_action(action_to_execute, parameters, current_gameboard)

    def make_bloodhound_phase_moves(self, current_gameboard):
        """
        :param current_gameboard: A dict. The global data structure representing the current game board.
        :return: An integer
        """
        print('We are in the bloodhound phase for '+self.player_name)
        print('lets remove disturbed water counters from the map')

        allowable_actions = self.compute_allowable_bloodhound_phase_actions(current_gameboard)

        code = 0
        action_to_execute, parameters = self.agent.make_bloodhound_phase_move(self, current_gameboard, allowable_actions, code)
        t = (action_to_execute, parameters)
        # add to game history
        current_gameboard['history']['function'].append(self.agent.make_bloodhound_phase_move)
        params = dict()
        params['player'] = self
        params['current_gameboard'] = current_gameboard
        params['allowable_moves'] = allowable_actions
        params['code'] = code
        current_gameboard['history']['param'].append(params)
        current_gameboard['history']['return'].append(t)

        if action_to_execute == null_action:
            return self._execute_action(action_to_execute, parameters, current_gameboard)

        return self._execute_action(action_to_execute, parameters, current_gameboard)

    def _execute_action(self, action_to_execute, parameters, current_gameboard):
        """
        if the action successfully executes, a success code will be returned. If it cannot execute, it will return code failure code.
        The most obvious reason this might happens is because you chose an action that is not an allowable action in your
        situation. It won't break the code. There may
        be cases when an action is allowable in principle but not in practice.
        :param action_to_execute: a function to execute. It must be a function inside action_choices
        :param parameters: a dictionary of parameters. These will be unrolled inside the action to execute.
        :return: An integer code that is returned by the executed action.
        """
        print('Executing _execute_action for '+ self.player_name)
        if parameters:
            p = action_to_execute(**parameters)
            # add to game history
            current_gameboard['history']['function'].append(action_to_execute)
            params = parameters.copy()
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(p)

            return p
        else:
            p = action_to_execute()
            # add to game history
            current_gameboard['history']['function'].append(action_to_execute)
            params = dict()
            current_gameboard['history']['param'].append(params)
            current_gameboard['history']['return'].append(p)

            return p
