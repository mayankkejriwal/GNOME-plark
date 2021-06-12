from simulator import james_pelican_agent
from simulator import panther_agent_v1
from simulator import pelican_agent_v1
from simulator import example_pelican_agent
from simulator import example_panther_agent
from simulator import gameplay
from simulator.novelty_distributions import *

import sys
import csv
import os
from collections import defaultdict
import numpy as np


def concluding_result(winner, res_dic):
    """
    Update winner result to dict
    :param winner: current winner
    :param res_dic: dict for saving results
    :return: res_dic
    """
    if not winner:
        res_dic['No Winner'] += 1
    else:
        res_dic[winner.player_name] += 1
    return res_dic


def output_csv(cnt, name, res_without_novelty, res_with_novelty, keys):
    """
    save result into csv format
    :param cnt: counter
    :param name: output file name
    :param res_without_novelty: dict of pre-novelty result
    :param res_with_novelty: dict of post-novelty result
    :param keys: winner names -> 'pelican', 'panther', or 'No Winner'
    :return:
    """
    folder_name = '../tournament_csv'
    file_name = folder_name + '/' + name
    try:
        os.makedirs(folder_name)
    except:
        print(f'Tournament folder already exist')

    with open(file_name, 'a') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|')
        if not cnt:
            first_row = ['Without Novelty'] + [''] * 3 + ['With Novelty']
            writer.writerow(first_row)
            second_row = [k + '1' for k in keys] + [''] + [k + '2' for k in keys]
            writer.writerow(second_row)
        writer.writerow([res_without_novelty[k] for k in keys] + [''] + [res_with_novelty[k] for k in keys])
    csvfile.close()
    print(f'Finish {cnt + 1} experiment...')
    print('==========================================================================================')


def play_tournament_with_novelty(cnt, tournament_log_folder=None, nov=None, meta_seed=0, num_games=100, novelty_index=50):
    """
    If run this function, a experiment would be run
    :param cnt: counter to record current number of experiment
    :param tournament_log_folder:
    :param nov: novelty to be injected
    :param meta_seed: seed number
    :param num_games: total number of games per tournament
    :param novelty_index: position to inject novelty
    :return:
    """
    res_without_novelty = defaultdict(float)
    res_with_novelty = defaultdict(float)

    np.random.seed(meta_seed)
    big_list = list(range(0, 1000000))
    np.random.shuffle(big_list)
    tournament_seeds = big_list[0:num_games]

    for combination in agent_combination:
        # Get current agents for Pelican/Panther
        player1, player2 = combination[0], combination[1]

        # Run the tournament
        for seed in range(0, novelty_index):
            winner = gameplay.play_game_in_tournament(game_seed=tournament_seeds[seed],
                                                      player1=player1,
                                                      player2=player2,
                                                      inject_novelty_function=None)
            res_without_novelty = concluding_result(winner, res_without_novelty)

        for seed in range(novelty_index, num_games):
            winner = gameplay.play_game_in_tournament(game_seed=tournament_seeds[seed],
                                                      player1=player1,
                                                      player2=player2,
                                                      inject_novelty_function=getattr(sys.modules[__name__], nov))
            res_with_novelty = concluding_result(winner, res_with_novelty)

        res_names = ('pelican', 'panther', 'No Winner')
        for key in res_names:
            res_without_novelty[key] = res_without_novelty[key] / novelty_index
            res_with_novelty[key] = res_with_novelty[key] / (num_games - novelty_index)
        print(f'Avg result without injecting novelty --> {", ".join([k + ": " + str(res_without_novelty[k]) for k in res_names])}')
        print(f'Avg result with injecting novelty --> {", ".join([k + ": " + str(res_with_novelty[k]) for k in res_names])}')
        # output_csv(cnt, 'james_example_two_layer.csv', res_without_novelty, res_with_novelty, res_names)


if __name__ == '__main__':
    # agent combination normally contains two agents per game
    agent_combination = [[james_pelican_agent, example_panther_agent]]

    # Four novelties we have currently
    # novelties = ['weapon_bay_size_change']
    # novelties = ['torpedo_re_attach']
    novelties = ['two_layer_property']
    # novelties = ['active_torpedo']

    # tournament setting
    novelty_index = 50
    num_games = 100

    for nov in novelties:
        print(f'Run the tournament with novelty {nov} at index {novelty_index}')
        for i in range(10):
            play_tournament_with_novelty(i, None, nov=nov, meta_seed=2, num_games=num_games, novelty_index=novelty_index)

