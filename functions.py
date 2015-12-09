from flask import request
import psycopg2
import psycopg2.extras
import secret
from timeit import default_timer as timer
DB_DSN = secret.DATABASE

def removekey(d, key):
    """
    removes a key from a dictionary and returns dictionary without that key
    :param d: dictionary to change
    :param key: key to remove
    :return: d but with key removed.
    """
    r = dict(d)
    del r[key]
    return r

def executeQuery(DB_DSN, sql, vars):
    """
    executes a query on the database
    :param DB_DSN: hostname of database to connect to
    :param sql: sql query
    :param vars: sql parameters vars
    :return: query output
    """
    conn = psycopg2.connect(dsn=DB_DSN)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    print sql % vars
    start = timer()
    cur.execute(sql, vars)
    end = timer()
    print "Query Executed in " + str(end - start) + " Seconds"
    output = cur.fetchall()
    cur.close()
    conn.close()
    return output

def get_teams(team_id, team_abbr):
    """
    gets teams from nba_teams
    :param team_id: team_id of team to fetch form database:
    :param team_abbr: abbreviation of team to fetch form database:
    :return: a dict of all kv pairs, key = team_id and value = dictionary of meta data
    """
    out = dict()
    team_id, team_abbr = request.args.get('id'), request.args.get('abbr')

    sql = "SELECT * FROM nba_teams"
    vars = tuple()

    if team_id != None and team_abbr == None:
        sql += " WHERE team_id = %s"
        vars = (team_id,)
    elif team_id == None and team_abbr != None:
        sql += "  WHERE abbreviation = %s"
        vars = (team_abbr,)
    elif team_id != None and team_abbr == None:
        sql += " WHERE team_id = %s and abbreviation = %s"
        vars = (team_id, team_abbr)

    try:
        rs = executeQuery(DB_DSN, sql, vars)
        for item in rs:
            out[item["team_id"]] = removekey(item, "team_id")

    except psycopg2.Error as e:
        print e.message

    return out

def get_movement(game_id, player_id):
    """
    gets movements of a certain player from nba_movement
    :param game_id: id of game to look in
    :param player_id: id of player to get movements for
    :return: list of movements containing x, y and clock information for every 40ms in game
    """
    out = dict()
    sql = "SELECT locations FROM nba_locations_new WHERE game_id = %s AND player_id = %s"
    vars = (game_id, player_id)
    try:
        rs = executeQuery(DB_DSN, sql, vars)
        out = rs[0]

    except psycopg2.Error as e:
        print e.message

    return out

def get_active_players(game_id):
    """
    gets movements of a certain player from nba_movement
    :param game_id: id of game to look in
    :param player_id: id of player to get movements for
    :return: list of movements containing x, y and clock information for every 40ms in game
    """
    out = dict()
    sql = "SELECT DISTINCT player_id FROM nba_locations_new WHERE game_id = %s"
    vars = (game_id,)
    try:
        rs = executeQuery(DB_DSN, sql, vars)
        out['active_players'] = rs

    except psycopg2.Error as e:
        print e.message

    return out



def get_games(movement, game_id):
    """
    gets movements of a certain player from nba_movement
    :param movement: string to determine whether to look only for games with movement data
    :param game_od: id of game to look for
    :return: dictionary of key value pairs with game information and players if possible.
    """
    out = dict()

    if movement == "true":
        table = "((SELECT DISTINCT game_id FROM nba_locations_new) a" \
                  " LEFT JOIN (SELECT * FROM nba_games) b on a.game_id = b.game_id) a"
    else:
        table = " nba_games a "


    sql = "SELECT * FROM " + table
    vars = tuple()

    if game_id:
        sql += " WHERE a.game_id = %s"
        vars = (game_id,)

    try:
        rs = executeQuery(DB_DSN, sql, vars)
        for item in rs:
            out[str(item['game_id'])] = {}
            for i, v in item.iteritems():
                # if i == "home_team" or i == "away_team":
                #     out[i] = {}
                #     out[i][str(i)] = v['players']
                if i != 'game_id':
                    if i =="game_date" or i=="game_time":
                        v = str(v)
                    out[str(item['game_id'])][str(i)] = v

        if game_id:
            sql = "SELECT home_team, away_team from nba_players WHERE game_id = %s"
            rs = executeQuery(DB_DSN, sql, vars)
            for item in rs:
                for i, v in item.iteritems():
                    # if i == "home_team" or i == "away_team":
                    #     out[i] = {}
                    #     out[i][str(i)] = v['players']
                    if i != 'game_id':
                        if i =="game_date" or i=="game_time":
                            v = str(v)
                        out[str(i)] = v

    except psycopg2.Error as e:
        print e.message

    return out
