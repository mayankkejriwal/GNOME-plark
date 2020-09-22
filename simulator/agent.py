from simulator.flag_config import flag_config_dict
# import logging
# logger = logging.getLogger('monopoly_simulator.logging_info.agent')


class Agent(object):
    def __init__(self,make_pelican_phase_move,make_madman_phase_move,make_maypole_phase_move,
                 make_panther_phase_move,make_bloodhound_phase_move,initialization_routine,agent_type):
        """

        """

        self.make_pelican_phase_move = make_pelican_phase_move
        self.make_madman_phase_move = make_madman_phase_move
        self.make_maypole_phase_move = make_maypole_phase_move
        self.make_panther_phase_move = make_panther_phase_move
        self.make_bloodhound_phase_move = make_bloodhound_phase_move
        self.initialization_routine = initialization_routine
        if agent_type != 'Panther' and agent_type != 'Pelican':
            print('the agent is neither a panther nor pelican...')
            raise Exception
        self.agent_type = agent_type
        self.is_running = False   #a flag which says if the agent is active or shutdown
        self._agent_memory = dict()  # a scratchpad for the agent
        self.init_position = None
        self.init_weapons_bay = None


    def startup(self, current_gameboard, indicator=None):
        """
        This function is called before simulating the game instance to startup the player agents by setting their is_running
        flag to true. This is done only after making sure that all the agent functions have been initialized.
        :param current_gameboard: the initial state of current_gameboard right after setting up the board.
        :param indicator: a string that can be used to indicate the type of game startup (like normal startup, restart, etc)
        :return: returns successful action code if all function handlers are intialized and after agent is started up. Any error in doing so results
        in a return value of failure code.
        """
        if self.make_pelican_phase_move == None:
            print("Agent not initialized properly. Returning failure_code.")
            return flag_config_dict['failure_code']
        if self.make_madman_phase_move == None:
            print("Agent not initialized properly. Returning failure_code.")
            return flag_config_dict['failure_code']
        if self.make_maypole_phase_move == None:
            print("Agent not initialized properly. Returning failure_code.")
            return flag_config_dict['failure_code']
        if self.make_panther_phase_move == None:
            print("Agent not initialized properly. Returning failure_code.")
            return flag_config_dict['failure_code']
        if self.make_bloodhound_phase_move == None:
            print("Agent not initialized properly. Returning failure_code.")
            return flag_config_dict['failure_code']

        self.initialization_routine(self, current_gameboard)


        self.is_running = True
        return flag_config_dict['successful_action']


    def shutdown(self):
        """
        This function is called to shutdown a running agent after the game terminates.
        :return: function returns successful action code is the agent is successfully shut down else return failure code. (if trying to shutdown an
        already shutdown agent.)
        """
        if self.is_running == False:
            print("Trying to shutdown an already shutdown agent. Returning -1.")
            return flag_config_dict['failure_code']
        else:
            self.is_running = False
            return flag_config_dict['successful_action']
