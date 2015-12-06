from flask import request
import psycopg2
import psycopg2.extras
import secret
from timeit import default_timer as timer

DB_DSN = secret.DATABASE



def removekey(d, key):
    r = dict(d)
    del r[key]
    return r

def executeQuery(DB_DSN, sql, vars):
    conn = psycopg2.connect(dsn=DB_DSN)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    start = timer()
    cur.execute(sql, vars)
    end = timer()
    print sql % vars
    print "Query Executed in " + str(end - start) + " Seconds"
    output = cur.fetchall()
    cur.close()
    conn.close()
    return output

def get_teams(team_id, team_abbr):
    """
    calculates the total number of restaurants in each borough
    :return: a dict of all kv pairs, key = borough and value = count
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

def get_all_games(game_id, team_id):
    """
    calculates the total number of restaurants in each borough
    :return: a dict of all kv pairs, key = borough and value = count
    """
    out = dict()
    sql = "SELECT * FROM nba_games"
    vars = tuple()

    if (game_id != None) and (team_id == None):
        sql += " WHERE game_id = %s"
        vars = (game_id,)
    elif (game_id == None) and (team_id != None):
        sql += " WHERE home_team_id = %s OR away_team_id = %s"
        vars = (team_id, team_id)
    elif (game_id != None) and (team_id != None):
        sql += " WHERE (home_team_id = %s OR away_team_id = %s) AND game_id = %s"
        vars = (team_id, team_id, game_id)
    try:
        rs = executeQuery(DB_DSN, sql, vars)
        for item in rs:
            out[str(item['game_id'])] = {}
            for i, v in item.iteritems():
                if i != 'game_id':
                    out[str(item['game_id'])][str(i)] = str(v)
    except psycopg2.Error as e:
        print e.message

    return out


def get_games(game_id, team_id, movement):
    out = dict()


    if game_id != None:
        players = ", home_team, away_team "
    else:
        players = ""

    if movement == "true":
        table = "((SELECT game_id" + players + " FROM nba_movement) a" \
                  " LEFT JOIN (SELECT * FROM nba_games) b on a.game_id = b.game_id)"
    else:
        table = " nba_games a "

    sql = "SELECT * FROM " + table
    vars = tuple()

    if game_id != None or team_id != None:
        sql += " WHERE"

    if game_id != None:
        sql += " a.game_id = %s"
        vars = vars + (game_id,)
        if team_id != None:
            sql += " AND"

    if team_id != None:
        sql += " (home_team_id = %s OR away_team_id = %s)"
        vars = vars + (team_id, team_id)


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
    except psycopg2.Error as e:
        print e.message

    return out


def get_movement(game_id, player_id):
    """
    calculates the total number of restaurants in each borough
    :return: a dict of all kv pairs, key = borough and value = count
    """
    out = dict()
    sql = "SELECT movement->%s as movement FROM nba_movement WHERE game_id = %s"
    vars = (player_id, game_id)
    try:
        rs = executeQuery(DB_DSN, sql, vars)
        out["movement"] = []
        for item in rs[0]["movement"]["rows"]:
            out["movement"].append({
                "x":item[2],
                "y":item[3],
                "g":int(item[4]),
                "c":round(item[5], 1) if item[5] != None else 0
            })

    except psycopg2.Error as e:
        print e.message

    return out
