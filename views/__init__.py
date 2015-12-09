from app import app
import functions
from flask import render_template, jsonify, request

@app.route('/')
def homepage():
    """
    :return: a json of teams
    """
    return render_template('home.html')



@app.route('/heatmap')
def heatmap():
    return render_template('heatmap.html')


@app.route('/nba/teams')
def get_teams():
    """
    :return: a json of teams
    """
    team_id, team_abbr = request.args.get('id'), request.args.get('abbr')
    out = functions.get_teams(team_id, team_abbr)
    return jsonify(out)


@app.route('/nba/games')
def get_games():
    """
    :return: a json of games based on input parameters
    """
    movement, game_id = request.args.get('movement'), request.args.get('game_id')
    out = functions.get_games(movement, game_id)

    return jsonify(out)


@app.route('/nba/movement')
def get_movement():
    """
    :return: json of movement information for player and game id from GET arguments
    """
    game_id, player_id = request.args.get('game_id'), request.args.get('player_id')
    out = functions.get_movement(game_id, player_id)

    return jsonify(out)


@app.route('/nba/players')
def get_active_players():
    """
    :return: json of players information for a given game id from GET arguments
    """
    game_id = request.args.get('game_id')
    out = functions.get_active_players(game_id)

    return jsonify(out)



