# Copyright 2018 Rhyan Arthur

""" Squad Maker web app written with Flask framework. """

import logging
import os
from logging.handlers import RotatingFileHandler
from flask import Flask, request, render_template, redirect, url_for, flash

from squad_maker_app.algorithms import make_squads_minimize_cumulative_delta_mean

SETTINGS_ENV_VAR = 'SQUAD_MAKER_SETTINGS'
PLAYER_SOURCE_CONFIG = 'PLAYER_SOURCE'
NUM_SQUADS_REQUEST_ARG = 'numSquads'
LOG_FILE = 'instance.log'
MAX_LOG_FILE_BYTES = 10000
MAX_LOG_FILE_BACKUPS = 1


def create_app():
    app = Flask(__name__)

    # configure logging
    log_handler = RotatingFileHandler(LOG_FILE, maxBytes=MAX_LOG_FILE_BYTES, backupCount=MAX_LOG_FILE_BACKUPS)
    log_handler.setLevel(logging.DEBUG if app.debug else logging.INFO)
    app.logger.addHandler(log_handler)

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
        waiting_list = get_all_players()
        waiting_list.sort(key=total_rating, reverse=True)
        return render_template('home.html', waiting_list=waiting_list,
                               num_squads_input_name=NUM_SQUADS_REQUEST_ARG)

    @app.route('/squad-maker')
    def make_squads():
        try:
            num_squads = get_num_squads_from_request(request)
            players = get_all_players()
            (squads, waiting_list) = make_squads_minimize_cumulative_delta_mean(num_squads, players)
            app.logger.info("Built %d squads with %d players on the waiting list" % (len(squads), len(waiting_list)))
            for squad in squads:
                squad.players.sort(key=total_rating, reverse=True)
            waiting_list.sort(key=total_rating, reverse=True)
            return render_template('squads.html', squads=squads, waiting_list=waiting_list)
        except ValueError as e:
            # A ValueError indicates a problem with one or more of the input arguments. We
            # want to show these types of errors to the user. All other errors/exceptions should
            # trigger a 5XX error
            app.logger.info("Got a ValueError while building squads: %s" % str(e))
            flash(str(e), 'error')
            return redirect(url_for('home'))

    @app.errorhandler(404)
    def handle_page_not_found(e):
        return render_template('not_found.html')

    def get_all_players():
        if PLAYER_SOURCE_CONFIG not in app.config:
            raise Exception("Missing required '%s' configuration variable" % PLAYER_SOURCE_CONFIG)
        players = app.config[PLAYER_SOURCE_CONFIG]()
        app.logger.info("Sourced data for %d players" % (len(players) if players else None))
        return players

    def total_rating(player):
        """ Sort players by cumulative skill rating """
        return player.skating + player.shooting + player.checking

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
