import psycopg2, psycopg2.extras
import get_nba_data
import settings
from flask.ext.compress import Compress

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
    query = 'DROP TABLE IF EXISTS nba_players'

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
    query = "CREATE TABLE nba_players (game_id TEXT UNIQUE, home_team JSON, away_team JSON)"
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
    conn = psycopg2.connect(dsn=DB_DSN)

    sql = 'SELECT game_id FROM nba_players'
    cur = conn.cursor()
    cur.execute(sql, vars)
    rs = cur.fetchall()
    game_ids = [str(item[0]) for item in rs]

    movement = get_nba_data.get_players(game_ids)

    while True:
        data = next(movement)
        try:
            print "uploading data"
            sql = 'INSERT INTO nba_players (game_id, home_team, away_team)' \
                    'VALUES (%s, %s, %s)'
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

    print "dropping table"
    drop_table()

    # create the db
    print "creating table"
    create_table()

    # insert the data
    print "inserting data"
    insert_data()
