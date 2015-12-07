from app import app
import functions
from flask import render_template, jsonify, request
from flask.ext.compress import Compress


@app.route('/')
def home():
    return render_template('home.html', methods=[{'value':'spectral', 'name': 'Spectral'}, {'name':'K-Means','value': 'kmeans'}, {'name':'Hierarchical', 'value': 'hierarchical'}])


def removekey(d, key):
    """
    calculates the total number of restaurants in each borough
    :return: a dict of all kv pairs, key = borough and value = count
    """
    r = dict(d)
    del r[key]
    return r


@app.route('/nba/teams')
def get_teams():
    """
    Returns meta data for all teams in database
    :return: a json of all kv pairs, key = team id and value = count
    """
    team_id, team_abbr = request.args.get('id'), request.args.get('abbr')
    out = functions.get_teams(team_id, team_abbr)
    return jsonify(out)

@app.route('/nba/games')
def get_games():
    """
    calculates the total number of restaurants in each borough
    :return: a dict of all kv pairs, key = borough and value = count
    """
    movement, game_id = request.args.get('movement'), request.args.get('game_id')
    out = functions.get_games(movement, game_id)

    return jsonify(out)


@app.route('/nba/movement')
def get_movement():
    """
    calculates the total number of restaurants in each borough
    :return: a dict of all kv pairs, key = borough and value = count
    """
    game_id, player_id = request.args.get('game_id'), request.args.get('player_id')
    out = functions.get_movement(game_id, player_id)

    return jsonify(out)

@app.route('/nba/players')
def get_players():
    """
    calculates the total number of restaurants in each borough
    :return: a dict of all kv pairs, key = borough and value = count
    """
    game_id = request.args.get('game_id')
    out = functions.get_players(game_id)

    return jsonify(out)

