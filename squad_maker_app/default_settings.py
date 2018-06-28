# Copyright 2018 Rhyan Arthur

""" Contains default application settings. """

from os.path import dirname, abspath, join
from squad_maker_app.data_sources import get_rest_data_source

# useful constants
APP_ROOT = dirname(abspath(__file__))
APP_STATIC = join(APP_ROOT, 'static')

# IMPORTANT: The production config file MUST override SECRET_KEY with a key that is actually secret (and unique)
SECRET_KEY = 'dev'

# By default read generated player data from json-generator.com.
# TODO: When the player REST API is available update this uri.
PLAYER_SOURCE = get_rest_data_source("http://www.json-generator.com/api/json/get/bVlwKzZWbm?indent=2")