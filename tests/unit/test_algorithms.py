# Copyright 2018 Rhyan Arthuri

import unittest
from squad_maker_app.models import Player, Squad
from squad_maker_app.algorithms import make_random_squads, make_squads_minimize_cumulative_delta_mean, DeltaMeanPlayerDecorator, \
    DeltaMeanSquadDecorator
from squad_maker_app.data_sources import generate_players


class TestSquadMaker(unittest.TestCase):

    ALGORITHMS = [make_random_squads, make_squads_minimize_cumulative_delta_mean]

    def test_zero_squads_error(self):
        for algorithm in self.ALGORITHMS:
            with self.subTest(algorithm=algorithm):
                with self.assertRaises(ValueError):
                    algorithm(num_squads=0, players=[])

    def test_not_enough_players_error(self):
        for algorithm in self.ALGORITHMS:
            with self.subTest(algorithm=algorithm):
                with self.assertRaises(ValueError):
                    players = generate_players(4)
                    algorithm(num_squads=5, players=players).run()

    def test_make_one_squad(self):
        for algorithm in self.ALGORITHMS:
            with self.subTest(algorithm=algorithm):
                num_squads = 1
                num_players = 18
                players = generate_players(num_players)
                (squads, waiting_list) = algorithm(num_squads, players)
                self.assertEqual(0, len(waiting_list))
                self.assertEqual(num_squads, len(squads))
                self.assertEqual(num_players, len(squads[0].players))

    def test_single_player_squads(self):
        for algorithm in self.ALGORITHMS:
            with self.subTest(algorithm=algorithm):
                num_squads = 5
                players = generate_players(num_squads)
                (squads, waiting_list) = algorithm(num_squads, players)
                self.assertEqual(num_squads, len(squads))
                for squad in squads:
                    self.assertEqual(1, len(squad.players))
                self.assertEqual(0, len(waiting_list))

    def test_waiting_list(self):
        for algorithm in self.ALGORITHMS:
            with self.subTest(algorithm=algorithm):
                num_squads = 5
                num_players = 22
                players = generate_players(num_players)
                (squads, waiting_list) = algorithm(num_squads, players)
                self.assertEqual(num_squads, len(squads))
                for squad in squads:
                    self.assertEqual(4, len(squad.players))
                self.assertEqual(2, len(waiting_list))


class TestDeltaMeanDecorators(unittest.TestCase):

    def test_get_decorated_player_attributes(self):
        player = Player('firstName', 'lastName', skating=100, shooting=5, checking=52)
        decorated_player = DeltaMeanPlayerDecorator(player, mean_skating=40, mean_shooting=40, mean_checking=50)
        # the attributes of Player should be accessible from the decorated object
        self.assertEqual('firstName', decorated_player.first_name)
        self.assertEqual('lastName', decorated_player.last_name)
        self.assertEqual(100, decorated_player.skating)
        self.assertEqual(5, decorated_player.shooting)
        self.assertEqual(52, decorated_player.checking)
        # test decorator methods
        self.assertEqual(60, decorated_player.delta_skating)
        self.assertEqual(-35, decorated_player.delta_shooting)
        self.assertEqual(2, decorated_player.delta_checking)
        self.assertEqual(97, decorated_player.cumulative_delta_mean)

    def test_get_decorated_squad_attributes(self):
        player1 = Player('name1', 'lastName1', skating=34, shooting=89, checking=10)
        player2 = Player('name2', 'lastName2', skating=0, shooting=55, checking=98)
        (mean_skating, mean_shooting, mean_checking) = (60, 55, 40)
        squad = Squad([DeltaMeanPlayerDecorator(player1, mean_skating, mean_shooting, mean_checking),
                       DeltaMeanPlayerDecorator(player2, mean_skating, mean_shooting, mean_checking)])
        decorated_squad = DeltaMeanSquadDecorator(squad.players)
        # the attributes of the Squad should be accessible from the decorated object
        self.assertEqual(squad.players, decorated_squad.players)
        self.assertEqual(squad.skating_average, decorated_squad.skating_average)
        self.assertEqual(squad.shooting_average, decorated_squad.shooting_average)
        self.assertEqual(squad.checking_average, decorated_squad.checking_average)
        # test decorator methods
        self.assertEqual(148, decorated_squad.cumulative_delta_mean)

    def test_double_player_decorator(self):
        player = Player('Happy', 'Gilmore', skating=10, shooting=99, checking=80)
        decorated_player = DeltaMeanPlayerDecorator(player, *(0, 0, 0))
        self.assertEqual(player, decorated_player.delegate)
        double_decorated_player = DeltaMeanPlayerDecorator(decorated_player, *(0, 0, 0))
        self.assertEqual(player, double_decorated_player.delegate)


if __name__ == '__main__':
    unittest.main()