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


def process_file(conn, table_name, file_object):
    SQL_STATEMENT = """
    COPY %s FROM STDIN WITH
        CSV
        DELIMITER AS ','
    """
    cursor = conn.cursor()
    cursor.copy_expert(sql=SQL_STATEMENT % table_name, file=file_object)
    conn.commit()
    cursor.close()

def drop_table():
    """
    drops the table 'restaurants' if it exists
    :return:
    """
    query = 'DROP TABLE IF EXISTS nba_locations'

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
    query = 'CREATE TABLE nba_locations (game_id TEXT, player_id TEXT, m_timestamp TEXT , x FLOAT' \
            ', y FLOAT, game_clock FLOAT, shot_clock FLOAT)'
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

    sql = 'SELECT DISTINCT game_id FROM nba_games'
    cur = conn.cursor()
    cur.execute(sql, vars)
    rs = cur.fetchall()
    all_game_ids = [str(item[0]) for item in rs]

    sql = 'SELECT DISTINCT game_id FROM nba_locations'
    cur = conn.cursor()
    cur.execute(sql, vars)
    rs = cur.fetchall()
    existing_game_ids = [str(item[0]) for item in rs]

    game_ids = [item for item in all_game_ids if item not in existing_game_ids]
    print game_ids

    movement = get_nba_data.get_location_data(game_ids)

    while True:
        try:
            print "uploading data"
            while True:
                data = next(movement)
                print "uploading"
                cur = conn.cursor()
                args_str = ','.join(cur.mogrify("(%s, %s, %s, %s, %s, %s, %s)", x) for x in data)
                cur.execute("INSERT INTO nba_locations (game_id, player_id, m_timestamp, x, y, game_clock, shot_clock)"
                            " VALUES " + args_str)
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

    print "dropping table"
    drop_table()

    #create the db
    print "creating table"
    create_table()

    # insert the data
    print "inserting data"
    insert_data()
