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
    drops the table 'restaurants' if it exists
    :return:
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
    creates a postgres table with columns ...
    :return:
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
    inserts the data using execute many
    :param data: a list of tuples with order ...
    :return:
    """
    games = get_nba_data.get_games()
    conn = psycopg2.connect(dsn=DB_DSN)
    for game, meta in games.iteritems():
        try:
            data = (game, meta["home_team_id"], meta["away_team_id"], meta["game_name"], meta["home_team_score"],
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
    # running this program as a main file will perform ALL the ETL
    # it will extract and transform the data from it file

    # print "transforming data"
    # data = transform_data(INPUT_DATA)

    print "dropping table"
    drop_table()

    # create the db
    print "creating table"
    create_table()

    # insert the data
    print "inserting data"
    insert_data()
