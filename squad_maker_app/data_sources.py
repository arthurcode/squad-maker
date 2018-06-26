# Copyright 2018 Rhyan Arthur

""" Contains utilities for reading and generating ``Player`` data.

Functions:
    get_rest_data_source: returns a function to GET ``Player`` JSON from a REST API uri.
    get_file_data_source: returns a function to read ``Player`` JSON from a local file.
    get_generated_data_source: returns a function that generates fake ``Player`` data for testing purposes.
    generate_players: generates the specified number of fake Player objects, for testing purposes.
"""

import json
import random
import requests
from squad_maker_app.models import Player

# Player JSON keys
PLAYERS_KEY = 'players'
ID_KEY = '_id'
FIRST_NAME_KEY = 'firstName'
LAST_NAME_KEY = 'lastName'
SKILLS_KEY = 'skills'
SKILL_TYPE_KEY = 'type'
SKILL_RATING_KEY = 'rating'
SKATING_SKILL = 'Skating'
SHOOTING_SKILL = 'Shooting'
CHECKING_SKILL = 'Checking'

DEFAULT_MIN_RATING = 20
DEFAULT_MAX_RATING = 100


def get_rest_data_source(uri):
    """ Returns a REST API source of ``Player`` data.

    It is assumed the REST API returns player data in the expected JSON format.

    Args:
        uri (str): The REST endpoint to get data from.

    Returns:
        func: Zero-argument function that GETs ``Player`` data from ``uri``.

    """
    def players_from_rest():
        response = requests.get(uri)
        response.raise_for_status()
        return parse_players_json(response.text)
    return players_from_rest


def get_file_data_source(filename):
    """ Returns a file source of ``Player`` data.

    It is assumed the file contains player data in the expected JSON format.

    Args:
        filename (str): The name of the file to read data from.

    Returns:
        func: Zero-argument function that reads ``Player`` data from the given file.

    """
    def players_from_file():
        with open(filename, 'r') as f:
            json_str = '\n'.join(f.readlines())
            return parse_players_json(json_str)
    return players_from_file


def parse_players_json(json_str):
    players_json = json.loads(json_str).get(PLAYERS_KEY)
    players_by_id = dict((p[ID_KEY], p) for p in players_json)  # removes duplicate entries
    return [_parse_player_json(p) for p in players_by_id.values()]


def _parse_player_json(player_json):
    try:
        first_name = player_json.get(FIRST_NAME_KEY, None)
        last_name = player_json.get(LAST_NAME_KEY, None)
        skills = dict([(s[SKILL_TYPE_KEY], s[SKILL_RATING_KEY]) for s in player_json[SKILLS_KEY]])
        return Player(first_name, last_name, skating=skills[SKATING_SKILL], shooting=skills[SHOOTING_SKILL],
                      checking=skills[CHECKING_SKILL])
    except Exception as e:
        # include the JSON map in the exception message for diagnostic purposes
        raise Exception("Failed to convert JSON map to Player object: '%s'" % player_json, e)


def get_generated_data_source(num_players, min_rating=DEFAULT_MIN_RATING, max_rating=DEFAULT_MAX_RATING):
    """ Returns a generated source of ``Player`` data.

    Each generated player is assigned a random skill rating for skating, shooting, and checking between
    ``min_rating`` and ``max_rating``.

    Args:
        num_players (int): The number of players to generate.
        min_rating (int): The minimum skill rating.
        max_rating (int): The maximum skill rating.

    Returns:
        func: Zero-argument function that generates ``num_players`` ``Player`` objects.

    """
    return lambda: generate_players(num_players, min_rating, max_rating)


def generate_players(num_players, min_rating=DEFAULT_MIN_RATING, max_rating=DEFAULT_MAX_RATING):
    generator = player_generator(min_rating, max_rating)
    return [next(generator) for _ in range(num_players)]


def player_generator(min_rating, max_rating):
    i = 1
    while True:
        first_name = "firstName%d" % i
        last_name = "lastName%d" % i

        def generate_rating():
            return random.randint(min_rating, max_rating)
        player = Player(first_name, last_name, skating=generate_rating(), shooting=generate_rating(),
                        checking=generate_rating())
        yield player
        i +=1



