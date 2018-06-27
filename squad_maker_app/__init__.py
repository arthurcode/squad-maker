# Copyright 2018 Rhyan Arthur

""" Squad Maker web app written with Flask framework. """

import os
from flask import Flask, request, render_template, redirect, url_for, flash

from squad_maker_app.algorithms import make_squads_minimize_cumulative_delta_mean

SETTINGS_ENV_VAR = 'SQUAD_MAKER_SETTINGS'
PLAYER_SOURCE_CONFIG = 'PLAYER_SOURCE'
NUM_SQUADS_REQUEST_ARG = 'numSquads'


def create_app():
    app = Flask(__name__)

    # load default settings, and override with values from a custom config file, if present.
    app.config.from_object('squad_maker_app.default_settings')
    app.config.from_envvar(SETTINGS_ENV_VAR, silent=True)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def home():
        # initially all players are on the waiting list
        return render_template('home.html', waiting_list=get_all_players(),
                               num_squads_input_name=NUM_SQUADS_REQUEST_ARG)

    @app.route('/squad-maker')
    def make_squads():
        try:
            num_squads = get_num_squads_from_request(request)
            players = get_all_players()
            (squads, waiting_list) = make_squads_minimize_cumulative_delta_mean(num_squads, players)
            return render_template('squads.html', squads=squads, waiting_list=waiting_list)
        except ValueError as e:
            # A ValueError indicates a problem with one or more of the input arguments. We
            # want to show these types of errors to the user. All other errors/exceptions should
            # trigger a 5XX error
            flash(str(e), 'error')
            return redirect(url_for('home'))

    def get_all_players():
        if PLAYER_SOURCE_CONFIG not in app.config:
            raise Exception("Missing required '%s' configuration variable" % PLAYER_SOURCE_CONFIG)
        return app.config[PLAYER_SOURCE_CONFIG]()

    return app


def get_num_squads_from_request(request):
    value = request.args.get(NUM_SQUADS_REQUEST_ARG, '')

    if value in ['', None]:
        raise ValueError("You must enter the number of squads to make.")

    try:
        num_squads = int(value)
    except ValueError:
        raise ValueError("'%s' is not a valid number of squads." % value)

    if num_squads == 0:
        raise ValueError("You must build at least one squad.")

    if num_squads < 0:
        raise ValueError("You cannot build a negative number of squads.")
    return num_squads
