import psycopg2, psycopg2.extras
import get_nba_data
import settings

# this is the set of functions I used to build my database
# the source of my data is ...
# i had to transform it first because ...
# here are also functions for dropping and creating the db


# DSN location of the AWS - RDS instance
DB_DSN = settings.DATABASE

def drop_table():
    """
    drops the table 'nba_games' if it exists
    """
    query = 'DROP TABLE IF EXISTS nba_games'

    try:
        conn = psycopg2.connect(dsn=DB_DSN)
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()
    except psycopg2.Error as e:
        print e.message
    else:
        cur.close()
        conn.close()

def create_table():
    """
    creates table nba_games
    """
    query = "CREATE TABLE nba_games " \
            "(game_id TEXT UNIQUE, home_team_id TEXT, away_team_id TEXT, game_name TEXT, home_team_score INT, " \
            "away_team_score INT, game_time TIME , game_date  DATE, attendance INT)"
    try:
        conn = psycopg2.connect(dsn=DB_DSN)
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()
    except psycopg2.Error as e:
        print e.message
    else:
        cur.close()
        conn.close()


def insert_data():
    """
    queries database for existing games and loads new games from stats.nba.com using get_nba_data
    """
    conn = psycopg2.connect(dsn=DB_DSN)

    #get game ids already in database
    sql = 'SELECT DISTINCT game_id FROM nba_games'
    cur = conn.cursor()
    cur.execute(sql, vars)
    rs = cur.fetchall()
    game_ids = [str(item[0]) for item in rs]

    #generator of new games
    games = get_nba_data.get_games(game_ids)
    while True:
        try:
            meta = next(games)
            data = (meta["game_id"], meta["home_team_id"], meta["away_team_id"], meta["game_name"], meta["home_team_score"],
                    meta["away_team_score"], meta["game_time"], meta["game_date"], meta["attendance"])
            print "uploading data"
            sql = 'INSERT INTO nba_games (game_id, home_team_id, away_team_id, game_name, home_team_score,' \
                  'away_team_score, game_time, game_date, attendance)' \
                    'VALUES (%s, %s, %s,%s,%s, %s, %s, %s, %s)'
            cur = conn.cursor()
            cur.execute(sql, data)
            conn.commit()
        except psycopg2.Error as e:
            print e
        except StopIteration:
            break
        else:
            cur.close()

    conn.close()

if __name__ == '__main__':

    # print "dropping table"
    # drop_table()
    #
    # # create the db
    # print "creating table"
    # create_table()

    # insert the data
    print "inserting data"
    insert_data()
