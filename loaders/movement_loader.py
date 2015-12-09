import psycopg2, psycopg2.extras
import get_nba_data

import settings
import csv



from psycopg2.extras import Json

# this is the set of functions I used to build my database
# the source of my data is ...
# i had to transform it first because ...
# here are also functions for dropping and creating the db


# DSN location of the AWS - RDS instance
DB_DSN = settings.DATABASE

def drop_table():
    """
    drops the table 'nba_locations' if it exists
    """
    query = 'DROP TABLE IF EXISTS nba_locations_new'

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
    creates table nba_locations
    """
    query = 'CREATE TABLE nba_locations_new (game_id TEXT, player_id TEXT, locations JSON)'
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
    queries database for existing games and loads new locations from stats.nba.com using get_nba_data
    """

    conn = psycopg2.connect(dsn=DB_DSN)
    sql = 'SELECT DISTINCT game_id FROM nba_games'
    cur = conn.cursor()
    cur.execute(sql, vars)
    rs = cur.fetchall()
    all_game_ids = [str(item[0]) for item in rs]

    sql = 'SELECT DISTINCT game_id FROM nba_locations_new'
    cur = conn.cursor()
    cur.execute(sql, vars)
    rs = cur.fetchall()
    existing_game_ids = [str(item[0]) for item in rs]

    game_ids = [item for item in all_game_ids if item not in existing_game_ids]
    print game_ids

    movement = get_nba_data.get_location_data(['0021500003'])

    while True:
        try:
            print "uploading data"
            while True:
                data = next(movement)
                for k, v in data[1].iteritems():
                    insert = data[0], k, Json(v)
                    print "uploading"
                    sql = 'INSERT INTO nba_locations_new (game_id, player_id, locations)' \
                        'VALUES (%s, %s, %s)'
                    cur.execute(sql, insert)
                    print "uploaded"
                    conn.commit()
        except psycopg2.Error as e:
            print e
        except StopIteration:
            break
        else:
            cur.close()
        break
    conn.close()

if __name__ == '__main__':
    # running this program as a main file will perform ALL the ETL
    # it will extract and transform the data from it file
    #
    # print "dropping table"
    # drop_table()
    #
    # #create the db
    # print "creating table"
    # create_table()

    # insert the data
    print "inserting data"
    insert_data()
