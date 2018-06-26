# Copyright 2018 Rhyan Arthur

import json
import unittest
from unittest.mock import patch, Mock

from squad_maker_app.data_sources import parse_players_json, PLAYERS_KEY, SKILLS_KEY, SKILL_TYPE_KEY, \
    SKILL_RATING_KEY, SKATING_SKILL, SHOOTING_SKILL, CHECKING_SKILL, ID_KEY, FIRST_NAME_KEY, LAST_NAME_KEY, \
    generate_players, get_rest_data_source


@patch('squad_maker_app.data_sources.requests')
class TestRestDataSource(unittest.TestCase):

    def test_happy_path(self, mock_requests):
        response_text = get_generated_json_str(num_players=10)
        mock_response = Mock()
        mock_response.text = response_text
        mock_requests.get = Mock(return_value=mock_response)
        uri = "http:hostname/path/to/endpoint/"

        player_supplier = get_rest_data_source(uri)
        players = player_supplier()
        self.assertEquals(10, len(players))
        mock_requests.get.assert_called_with(uri)

    def test_failed_request(self, mock_requests):
        mock_response = Mock()
        mock_response.raise_for_status = Mock(side_effect=Exception("boom!"))
        mock_requests.get = Mock(return_value=mock_response)
        uri = "bogus/uri"
        player_supplier = get_rest_data_source(uri)

        with self.assertRaisesRegex(Exception, "boom!"):
            player_supplier()


class TestParsePlayersJson(unittest.TestCase):

    def test_parse_empty_response(self):
        json_str = json.dumps(_get_players_dict([]))
        players = parse_players_json(json_str)
        self.assertEqual(0, len(players))

    def test_duplicate_players_in_json(self):
        player_dict = _get_player_dict('id', 'firstName', 'lastName', 40, 33, 78)
        players_json = json.dumps(_get_players_dict([player_dict, player_dict]))
        players = parse_players_json(players_json)
        self.assertEqual(1, len(players))

    def test_parse_mixed_format_ratings(self):
        player_dict = _get_player_dict('id', 'firstName', 'lastName', 33.5, 6, "23")
        players_json = json.dumps(_get_players_dict([player_dict]))
        players = parse_players_json(players_json)
        self.assertEqual(1, len(players))
        player = players[0]
        self.assertEqual(33.5, player.skating)
        self.assertEqual(6, player.shooting)
        self.assertEqual(23, player.checking)

    def test_parse_missing_rating_error(self):
        player_dict = _get_player_dict('id', 'firstName', 'lastName', 0, 0, 0)
        player_dict[SKILLS_KEY] = []
        players_json = json.dumps(_get_players_dict([player_dict]))
        with self.assertRaises(Exception):
            parse_players_json(players_json)

    def test_parse_missing_name(self):
        player_dict = _get_player_dict('id', '', '', 1, 2, 3)
        del(player_dict[FIRST_NAME_KEY])
        del(player_dict[LAST_NAME_KEY])
        players_json = json.dumps(_get_players_dict([player_dict]))
        players = parse_players_json(players_json)
        self.assertEqual(1, len(players))
        self.assertIsNone(players[0].first_name)
        self.assertIsNone(players[0].last_name)


def get_generated_json_str(num_players):
    """
    Generates the given number of players and then transforms the data to an equivalent JSON response.

    Args:
        num_players: the number of players to generates.

    Returns:
        str: the JSON players response.

    """
    players = generate_players(num_players)
    json_dict = _get_players_dict([_player_to_json_dict(p) for p in players])
    return json.dumps(json_dict)


def _get_players_dict(player_dicts):
    return {PLAYERS_KEY: player_dicts}


def _get_player_dict(id, first_name, last_name, skating, shooting, checking):
    skills = [
        {SKILL_TYPE_KEY: SKATING_SKILL, SKILL_RATING_KEY: skating},
        {SKILL_TYPE_KEY: SHOOTING_SKILL, SKILL_RATING_KEY: shooting},
        {SKILL_TYPE_KEY: CHECKING_SKILL, SKILL_RATING_KEY: checking}
    ]
    player = {
        ID_KEY: str(id),
        FIRST_NAME_KEY: first_name,
        LAST_NAME_KEY: last_name,
        SKILLS_KEY: skills
    }
    return player


def _player_to_json_dict(player):
    return _get_player_dict(id(player), player.first_name, player.last_name, player.skating, player.shooting,
                           player.checking)


