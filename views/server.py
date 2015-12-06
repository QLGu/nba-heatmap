from flask import Flask, request, jsonify
import get_json_data
# DSN location of the AWS - RDS instance

app = Flask(__name__)

def removekey(d, key):
    """
    calculates the total number of restaurants in each borough
    :return: a dict of all kv pairs, key = borough and value = count
    """
    r = dict(d)
    del r[key]
    return r

@app.route('/')
def default():
    """
    calculates the total number of restaurants in each borough
    :return: a dict of all kv pairs, key = borough and value = count
    """
    output = dict()

    # nothing is going on here
    output['message'] = 'Welcome to the test app!'

    return jsonify(output)

@app.route('/nba/teams')
def get_teams():
    """
    Returns meta data for all teams in database
    :return: a json of all kv pairs, key = team id and value = count
    """
    team_id, team_abbr = request.args.get('id'), request.args.get('abbr')
    out = get_json_data.get_teams(team_id, team_abbr)
    return jsonify(out)

@app.route('/nba/games')
def get_games():
    """
    calculates the total number of restaurants in each borough
    :return: a dict of all kv pairs, key = borough and value = count
    """
    game_id, team_id, movement = request.args.get('game_id'), request.args.get('team_id'), request.args.get('movement')
    out = get_json_data.get_games(game_id, team_id, movement)

    return jsonify(out)


@app.route('/nba/movement')
def get_movement():
    """
    calculates the total number of restaurants in each borough
    :return: a dict of all kv pairs, key = borough and value = count
    """
    game_id, player_id = request.args.get('game_id'), request.args.get('player_id')
    out = get_json_data.get_movement(game_id, player_id)

    return jsonify(out)

# @app.route('/nba/movement_games/')
# def get_movement_games():
#     game_id = request.args.get('game_id')
#     out = get_json_data.get_movement_games(game_id)
#     return jsonify(out)

if __name__ == "__main__":
    app.debug = True # only have this on for debugging!
    app.run(host='0.0.0.0') # need this to access from the outside world!
