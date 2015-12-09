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
    drops the table 'nba_teams' if it exists
    """
    query = 'DROP TABLE IF EXISTS nba_teams'

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
    query = "CREATE TABLE nba_teams " \
            "(team_id TEXT UNIQUE, team_name TEXT, abbreviation TEXT, city TEXT, division TEXT, conference TEXT, " \
            "division_rank INT, conference_rank INT,  wins INT, losses INT, first_appeared INT, last_appeared INT)"
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
    loads new teams from stats.nba.com into nba_teams using get_nba_data
    """
    teams = get_nba_data.get_teams()
    conn = psycopg2.connect(dsn=DB_DSN)
    for team, meta in teams.iteritems():
        try:
            data = (team, meta["name"], meta["abbreviation"], meta["city"], meta["division"], meta["conference"],
                    meta["division-rank"], meta["conference-rank"], meta["wins"], meta["losses"],
                    meta["first-appeared"], meta["last-appeared"])
            print "uploading data"
            sql = 'INSERT INTO nba_teams (team_id, team_name, abbreviation, city, division, conference, division_rank,'\
                  'conference_rank, wins, losses, first_appeared, last_appeared)' \
                'VALUES (%s, %s, %s,%s,%s, %s, %s, %s, %s, %s, %s, %s)'
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
