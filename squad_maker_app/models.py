# Copyright 2018 Rhyan Arthur

""" Contains the data models for the squad maker application.

Classes:
    Player: Represents a hockey player.
    Squad:  Represents a hockey squad (team).

Functions:
    to_rating: Converts a value to a numerical skill rating.
"""


class Player:
    """ Represents a hockey player with skill ratings for skating, shooting, and checking. """

    def __init__(self, first_name, last_name, skating, shooting, checking):
        """ Creates a hockey player with ratings for each of the skating, shooting, and checking skills.

        Args:
            first_name (str): The player's first name.
            last_name (str): The player's last name.
            skating (float): The player's skating rating expressed as a numeric value >= 0.
            shooting (float): The player's shooting rating expressed as a numeric value >= 0.
            checking (float): The player's checking rating expressed as a numeric value >= 0.

        Raises:
            ValueError: if ``skating``, ``shooting``, or ``checking`` cannot be converted to a valid numerical
                        rating larger than or equal to zero.

        """
        self.first_name = first_name
        self.last_name = last_name
        self.skating = to_rating(skating)
        self.shooting = to_rating(shooting)
        self.checking = to_rating(checking)


class Squad:
    """ Represents a hockey squad made up of zero or more players. """

    def __init__(self, players=None):
        """
        Creates a hockey squad with the given players.

        Args:
            players (list): The players to add to the squad initially. May be empty or None.
        """
        self.players = players or []

    @property
    def skating_average(self):
        """ Calculates the average skating rating for all players in the squad.

        Returns:
            float: The average skating rating, or None if there are no players in the squad.
        """
        return self._get_average_rating(lambda p: p.skating)

    @property
    def shooting_average(self):
        """ Calculates the average shooting rating for all players in the squad.

        Returns:
            float: The average shooting rating, or None if there are no players in the squad.
        """
        return self._get_average_rating(lambda p: p.shooting)

    @property
    def checking_average(self):
        """ Calculates the average checking rating for all players in the squad.

        Returns:
            float: The average checking rating, or None if there are no players in the squad.
        """
        return self._get_average_rating(lambda p: p.checking)

    def _get_average_rating(self, rating_supplier):
        if not self.players:
            return None
        ratings = [rating_supplier(p) for p in self.players]
        return sum(ratings) / len(ratings)


def to_rating(value):
    """
    Converts the given value to a valid numerical skill rating.

    Args:
        value (str, int, or float): The value to convert.

    Returns:
        float: The converted value.

    Raises:
        ValueError: If ``value`` cannot be converted to a float, or if the converted value is less than zero.
    """
    if type(value) not in [int, float, str]:
        raise ValueError("Cannot convert %s value '%s' to a rating. Only str and numerical types are allowed."
                         % (type(value), value))
    try:
        rating = float(value)
    except ValueError as e:
        raise ValueError("Failed to convert '%s' to a numerical rating" % value, e)
    if rating < 0:
        raise ValueError("Invalid rating: '%s'. Ratings must be larger than or equal to zero." % value)
    return rating