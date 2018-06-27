# Copyright 2018 Rhyan Arthur

""" Contains algorithms for organizing players on a waiting list into squads.

Functions:
    make_random_squads: builds squads by choosing players at random (used only as a baseline)
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

