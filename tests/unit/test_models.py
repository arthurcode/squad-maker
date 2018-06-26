# Copyright 2018 Rhyan Arthur

import unittest
from squad_maker_app.models import to_rating, Player, Squad


class TestSquad(unittest.TestCase):

    def test_empty_squad(self):
        squad = Squad()
        self.assertIsNone(squad.skating_average)
        self.assertIsNone(squad.shooting_average)
        self.assertIsNone(squad.checking_average)

    def test_single_player_squad(self):
        player = Player('Dwayne', 'Johnson', skating=10, shooting=20, checking=30)
        squad = Squad([player])
        self.assertEqual(player.skating, squad.skating_average)
        self.assertEqual(player.shooting, squad.shooting_average)
        self.assertEqual(player.checking, squad.checking_average)

    def test_multi_player_squad(self):
        player1 = Player('Richard', 'Wagner', skating=20, shooting=55, checking=25)
        player2 = Player('Fred', 'Couples', skating=10, shooting=5, checking=30)
        player3 = Player('Geena', 'Davis', skating=90, shooting=30, checking=5)
        squad = Squad([player1, player2, player3])
        self.assertEqual(40, squad.skating_average)
        self.assertEqual(30, squad.shooting_average)
        self.assertEqual(20, squad.checking_average)

    def test_modify_players(self):
        squad = Squad()
        self.assertIsNone(squad.skating_average)
        self.assertIsNone(squad.shooting_average)
        self.assertIsNone(squad.checking_average)

        new_player = Player('Brody', 'Harrison', skating=10, shooting=15, checking=22)
        squad.players.append(new_player)
        self.assertEqual(10, squad.skating_average)
        self.assertEqual(15, squad.shooting_average)
        self.assertEqual(22, squad.checking_average)


class TestPlayer(unittest.TestCase):

    def test_to_rating(self):
        self.assertEqual(1, to_rating(1))
        self.assertEqual(1.5, to_rating(1.5))
        self.assertEqual(38.2, to_rating('38.2'))
        self.assertEqual(0, to_rating('0'))

    def test_to_rating_non_numerical_error(self):
        self._assert_to_rating_raises_value_error(None)
        self._assert_to_rating_raises_value_error("notANumber")
        self._assert_to_rating_raises_value_error([1,2])
        self._assert_to_rating_raises_value_error(True)
        self._assert_to_rating_raises_value_error("1.2a")

    def test_to_rating_negative_error(self):
        self._assert_to_rating_raises_value_error(-5)
        self._assert_to_rating_raises_value_error('-38.2')

    def _assert_to_rating_raises_value_error(self, value):
        with self.assertRaises(ValueError):
            to_rating(value)

    def test_make_player(self):
        player = Player('FirstName', 'LastName', skating=25.0, shooting='78', checking=0)
        self.assertEqual('FirstName', player.first_name)
        self.assertEqual('LastName', player.last_name)
        self.assertEqual(25, player.skating)
        self.assertEqual(78, player.shooting)
        self.assertEqual(0, player.checking)

    def test_make_player_missing_name(self):
        # since player name isn't strictly necessary to run our squad maker algorithm we don't have
        # any restrictions on the allowed player name
        player = Player(None, None, skating=55, shooting=8, checking=38.2)
        self.assertIsNone(player.first_name)
        self.assertIsNone(player.last_name)


if __name__ == '__main__':
    unittest.main()