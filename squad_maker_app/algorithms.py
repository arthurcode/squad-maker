# Copyright 2018 Rhyan Arthur

""" Contains algorithms for organizing players on a waiting list into squads.

Functions:
    make_random_squads: builds squads by choosing players at random (used only as a baseline)
    make_squads_minimize_cumulative_delta_mean: builds squads by attempting to minimize the cumulative delta
        mean of each squad.
"""

from math import floor
from random import shuffle
from squad_maker_app.models import Squad


def make_random_squads(num_squads, players):
    """
    Makes squads by choosing players at random, without regard for their individual skill ratings.

    This algorithm isn't intended to be used in production, but it will serve as a useful baseline for
    evaluating other potential algorithms.

    Args:
        num_squads (int): The number of squads to build.
        players list(``Player``): The list of players to choose from.

    Returns:
        list(``Squad``), list(``Player``): A (squads, waiting_list) tuple.

    """
    _validate_arguments(num_squads, players)
    waiting_list = list(players)
    shuffle(waiting_list)
    squads = []
    players_per_squad = get_players_per_squad(num_squads, players)
    for _ in range(num_squads):
        squad = Squad([waiting_list.pop(0) for _ in range(players_per_squad)])
        squads.append(squad)
    return squads, waiting_list


def _validate_arguments(num_squads, players):
    if num_squads == 0:
        raise ValueError("You must build at least one squad.")

    if num_squads < 0:
        raise ValueError("You cannot build a negative number of squads.")

    if get_players_per_squad(num_squads, players) < 1:
        raise ValueError("There are not enough players to build %d squads. "
                         "You have %d players but need at least %d players."
                         % (num_squads, len(players), num_squads))


def get_players_per_squad(num_squads, players):
    """
    Calculates the number of players on each squad. Each squad must have the same number of players.

    Args:
        num_squads (int): The number of squads to build.
        players (list): The list of players on the waiting list.

    Returns:
        int: the number of players per squad.

    """
    return floor(len(players) / num_squads)


def make_squads_minimize_cumulative_delta_mean(num_squads, players):
    """ Makes closely matched squads from the given set of players.

    Algorithm steps:
        1. Calculate S(i) - Mean(i) for each player, where S(i) is the player's rating for the i-th skill, and Mean(i)
           is the mean value of the i-th skill over all players. S(i) - Mean(i) = Delta(i)
        2. Calculate the cumulative delta mean for each player. The cumulative delta mean is the sum of |Delta(i)|
           for each of the player's i skills.
        3. Sort the players in order of descending cumulative delta mean.
        4. If applicable, place the players with the largest cumulative delta mean on the waiting list. These are our
           biggest outliers.
        5. If players were moved to the waiting list, repeat steps (1-3) on the reduced set of players. We want
           to recalculate Delta(i) and the cumulative delta mean for each player with the outliers removed.
        6. Take the N players with the largest cumulative delta mean, and assign 1 to each of the N squads.
        7. While there are players left, round robin through each of the N squads and pick the 'best fit' available
           player and add it to the squad. The best fit player is the player who results in the lowest cumulative
           delta mean for the squad.

    Args:
        num_squads (int): The number of squads to make.
        players (list): The available players.

    Returns:
        list(``Squad``), list(``Player``): A (squads, waiting_list) tuple.

    """
    _validate_arguments(num_squads, players)
    waiting_list = []

    if num_squads == players:
        # handle special case where each squad has a single player and the waiting list is empty
        return [Squad([p]) for p in players], waiting_list

    players = _decorate_players_with_delta_mean_data(players)
    players.sort(key=lambda p: p.cumulative_delta_mean, reverse=True)

    players_per_squad = get_players_per_squad(num_squads, players)
    players_on_wait_list = len(players) - players_per_squad*num_squads
    waiting_list = [players.pop(0) for _ in range(players_on_wait_list)]

    if len(waiting_list) > 0:
        # recalculate the means and re-decorate with delta mean data now that the outliers are removed
        players = _decorate_players_with_delta_mean_data(players)
        players.sort(key=lambda p: p.cumulative_delta_mean, reverse=True)

    # initialize the required number of squads, each with one of the outlier players
    squads = [DeltaMeanSquadDecorator([players.pop(0)]) for _ in range(num_squads)]
    while len(players) > 0:
        for squad in squads:
            _append_best_fit_for_squad(squad, players)
    return squads, waiting_list


def _decorate_players_with_delta_mean_data(players):
    (mean_skating, mean_shooting, mean_checking) = _get_mean_ratings(players)
    return [DeltaMeanPlayerDecorator(p, mean_skating, mean_shooting, mean_checking) for p in players]


def _append_best_fit_for_squad(squad, player_data):
    minimum_delta = None
    best_fit_index = None

    for i in range(len(player_data)):
        player = player_data[i]
        # add the player to the squad and calculate the new cumulative delta mean
        squad.players.append(player)
        new_delta = squad.cumulative_delta_mean
        # restore the squad to its original membership
        squad.players.pop(-1)

        if not minimum_delta:
            minimum_delta = new_delta
            best_fit_index = i
        elif new_delta < minimum_delta:
            minimum_delta = new_delta
            best_fit_index = i
    # add the player to the squad that minimizes the cumulative delta mean of the squad
    squad.players.append(player_data.pop(best_fit_index))


def _get_mean_ratings(players):
    num_players = len(players)
    skill_array = [[p.skating, p.shooting, p.checking] for p in players]
    return (sum(t)/num_players for t in zip(*skill_array))


class DeltaMeanPlayerDecorator:
    """ Decorates a Player object with delta mean data for each skill. """

    def __init__(self, player, mean_skating, mean_shooting, mean_checking):
        """ Decorates the given Player with delta mean data for skating, shooting, and checking.

        Args:
            player (``Player``): The player to decorate.
            mean_skating: The average skating rating over all players.
            mean_shooting: The average shooting rating over all players.
            mean_checking: The average checking rating over all players.
        """
        if hasattr(player, 'delegate'):
            # already decorated, need to unwrap
            self.delegate = player.delegate
        else:
            self.delegate = player
        self.delta_skating = self.delegate.skating - mean_skating
        self.delta_shooting = self.delegate.shooting - mean_shooting
        self.delta_checking = self.delegate.checking - mean_checking

    @property
    def cumulative_delta_mean(self):
        """ Returns the sum of the absolute values of the delta mean for each skill.

        The larger the cumulative delta mean, the further this player is from a perfectly average player.

        Returns:
            float: The cumulative delta mean.

        """
        return abs(self.delta_skating) + abs(self.delta_shooting) + abs(self.delta_checking)

    def __getattr__(self, item):
        # expose the existing attributes of the delegate on the decorated object
        return getattr(self.delegate, item)


class DeltaMeanSquadDecorator:
    """ Decorates a squad object with cumulative delta mean data. """

    def __init__(self, players):
        """ Creates a new ``Squad`` from the given players and decorates it with cumulative delta mean data.

        Args:
            players (list): The players in the ``Squad``.
        """
        self.delegate = Squad(players)

    @property
    def cumulative_delta_mean(self):
        """ Calculates the cumulative delta mean of the squad.

        The cumulative delta mean of a squad is calculated by summing each player's Delta(i) together to
        get Sum(Delta(i)) for each skill, i. Then the absolute values of each (Sum(Delta(i)) are summed together
        to get the cumulative delta mean.

        Returns:
            float: The cumulative delta mean.

        """
        delta_array = [[p.delta_skating, p.delta_shooting, p.delta_checking] for p in self.delegate.players]
        delta_sums = (sum(t) for t in zip(*delta_array))
        return sum([abs(delta) for delta in delta_sums])

    def __getattr__(self, item):
        # expose the existing attributes of the delegate on the decorated object
        return getattr(self.delegate, item)

