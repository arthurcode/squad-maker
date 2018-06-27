# Copyright 2018 Rhyan Arthur

""" Contains default application settings. """

from os.path import dirname, abspath, join
from squad_maker_app.data_sources import get_file_data_source

# useful constants
APP_ROOT = dirname(abspath(__file__))
APP_STATIC = join(APP_ROOT, 'static')

# IMPORTANT: The production config file MUST override SECRET_KEY with a key that is actually secret (and unique)
SECRET_KEY = 'dev'

# By default read player data from a local file. Once the REST API is available this can
# be swapped out for a REST data source.
PLAYER_SOURCE = get_file_data_source(join(APP_STATIC, 'players.json'))