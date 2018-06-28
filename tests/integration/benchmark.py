#!/usr/bin/env python
# Copyright 2018 Rhyan Arthur

""" Benchmarks the squad maker algorithm by measuring squad skill variance for a number of generated data sets. """

import time
from math import floor
from squad_maker_app.data_sources import get_generated_data_source
from squad_maker_app.algorithms import make_random_squads, make_squads_minimize_cumulative_delta_mean

BENCHMARK_ALGORITHM = make_random_squads


class Experiment:

    def __init__(self, players, num_squads, algorithm):
        self.players = players
        self.num_squads = num_squads
        self.algorithm = algorithm
        self.benchmark_variance = None
        self.test_variance = None

    def run(self):
        self.benchmark_variance = self._run(BENCHMARK_ALGORITHM)
        self.test_variance = self._run(self.algorithm)

    def _run(self, algorithm):
        (squads, waiting_list) = algorithm(self.num_squads, self.players)
        return get_average_variance_between_squads(squads)


def get_average_variance_between_squads(squads):
    # the lower the variance in average ratings between squads, the better our algorithm is performing
    skills = [lambda s: s.skating_average,
              lambda s: s.shooting_average,
              lambda s: s.checking_average]
    average_variance = sum([get_variance(squads, s) for s in skills]) / len(skills)
    return average_variance


def get_variance(squads, get_skill_rating):
    num_squads = len(squads)
    mean = sum([get_skill_rating(s) for s in squads]) / num_squads
    variance = sum([(get_skill_rating(s) - mean)**2 for s in squads]) / num_squads
    return variance


def get_data_sources():
    return [get_generated_data_source(i) for i in [20,30,40,50,60,70,80,90,100]]


if __name__ == '__main__':
    experiments = []

    for player_source in get_data_sources():
        players = player_source()
        # we always want to build a minimum of 2 squads, and we always want at least 2 players per squad.
        # building single person squads isn't a good measure of what our algorithm can do because the variance
        # will be relatively fixed
        num_squads_trials = range(2, floor(len(players) / 2))
        experiments.extend([Experiment(players, n, make_squads_minimize_cumulative_delta_mean)
                            for n in num_squads_trials])

    start = time.time()
    for e in experiments:
        e.run()
    end = time.time()
    num_experiments = len(experiments)
    benchmark_variance = sum([e.benchmark_variance for e in experiments]) / num_experiments
    test_variance = sum([e.test_variance for e in experiments]) / num_experiments

    print("Ran %d experiments in %f seconds" % (num_experiments, end - start))
    print("Average benchmark variance: %f" % benchmark_variance)
    print("Average variance for '%s' algorithm: %f" % (make_squads_minimize_cumulative_delta_mean.__name__,
                                                       test_variance))