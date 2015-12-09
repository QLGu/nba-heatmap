import requests
import json
from psycopg2.extras import Json
import datetime
from collections import defaultdict

from itertools import chain

def merge_two_dicts(x, y):
    '''Given two dicts, merge them into a new dict as a shallow copy.'''
    z = x.copy()
    z.update(y)
    return z

def get_teams():
    """
    load the whole set of data into a data structure and THEN find the k:v
    :return: dictionary keys as team id, value dictionary of meta information
    """
    teams = {}

    url = "http://stats.nba.com/stats/leaguedashteamstats?Conference=&DateFrom=&DateTo=&Division=&" \
          "GameScope=&GameSegment=&LastNGames=0&LeagueID=00&Location=&MeasureType=Base&Month=0&" \
          "OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0&PlayerExperience=&" \
          "PlayerPosition=&PlusMinus=N&Rank=N&Season=2015-16&SeasonSegment=&SeasonType=Regular+Season&" \
          "ShotClockRange=&StarterBench=&TeamID=0&VsConference=&VsDivision="

    response = requests.get(url)
    table = response.json()["resultSets"][0]["rowSet"]

    team_ids = []

    for row in table:
        team_ids.append(str(row[0]))

    for team_id in team_ids:
        if team_id not in teams.keys():
            url = "http://stats.nba.com/stats/teaminfocommon?LeagueID=00&SeasonType=Regular+Season&" \
                  "TeamID="+str(team_id)+"&season=2015-16"
            response = requests.get(url)
            table = response.json()["resultSets"][0]["rowSet"][0]
            print table
            teams[team_id] = {
                "city": table[2],
                "conference": table[5],
                "division": table[6],
                "abbreviation": table[4],
                "first-appeared": table[13],
                "last-appeared": table[14],
                "wins": table[8],
                "losses": table[9],
                "division-rank": table[12],
                "conference-rank": table[11],
                "name": table[2] + " " + table[3]
            }

    with open('teams.json', 'w') as outfile:
        json.dump(teams, outfile, sort_keys=True, indent=4, separators=(',', ': '))

    return teams

# get_teams()

def get_games(completed_games):
    """
    load the whole set of data into a data structure and THEN find the k:v
    :param list of games to ignore:
    :return: dictionary keys as team id, value dictionary of meta information
    """

    url = "http://stats.nba.com/stats/leaguegamelog?Counter=1000&Direction=DESC&LeagueID=00&PlayerOrTeam=T&" \
          "Season=2015-16&SeasonType=Regular+Season&Sorter=PTS"
    response = requests.get(url)
    game_ids = [str(row[4]) for row in response.json()["resultSets"][0]["rowSet"]]
    for index, game_id in enumerate(game_ids):
        if game_id not in completed_games:
            url = "http://stats.nba.com/stats/boxscoresummaryv2?GameID="+str(game_id)
            try:
                response = requests.get(url)
                table = response.json()["resultSets"]
                game_info = table[4]["rowSet"][0]
                game_scores = table[5]["rowSet"]
                stats_available = table[8]["rowSet"][0][2] + table[8]["rowSet"][0][3]
                if stats_available == 2:
                    yield {
                        "game_id": game_id,
                        "attendance": game_info[1],
                        "game_date": datetime.datetime.strptime(game_info[0], '%A, %B %d, %Y').strftime('%m-%d-%y'),
                        "game_time": game_info[2].split(":")[0] + ":" + str(int(game_info[2].split(":")[1]) % 60),
                        "home_team_id": game_scores[0][3],
                        "away_team_id": game_scores[1][3],
                        "home_team_score": game_scores[0][22],
                        "away_team_score": game_scores[1][22],
                        "game_name": game_scores[1][5] + " " + game_scores[1][6] +
                                     " @ " + game_scores[0][5] + " " + game_scores[0][6]
                    }
                else:
                    print "No Tracking Information Available: " + str(game_id)
            except KeyError:
                print str(game_id) + "error"


def get_players(completed_games):
    """
    scrapes players for certain games from stats.nba.com
    :param list of games to ignore:
    :return: pair of dictionaries containing information on home and away players
    """
    game_ids = get_games()

    for game_id in game_ids:
        if game_id not in completed_games:
            current_event = 1
            header = False
            while header is False:
                url = "http://stats.nba.com/stats/locations_getmoments/?eventid=%s&gameid=" + str(game_id)
                try:
                    response = requests.get(url % (current_event, ))
                    header = True
                    yield (game_id, Json(response.json()["home"]), Json(response.json()["visitor"]))

                except ValueError:
                    pass
                except KeyError:
                    pass
                finally:
                    current_event += 1
        else:
            pass
            print "Skipping game id " + str(game_id)



def get_location_data(game_ids):
    """
    scrapes location data for certain games from stats.nba.com
    :param list of games to ignore:
    :return: generator object which yields list of tuples containing location information for 10 moments
    """
    for game_id in game_ids:
        current_moment = []
        done = []
        in_a_row = 0
        current_event = 0
        output = dict()
        while True:
            print current_event
            try:
                url = "http://stats.nba.com/stats/locations_getmoments/?eventid=%s&gameid=" + str(game_id)
                response = requests.get(url % current_event)
                moments = response.json()["moments"]
                for moment in moments:
                    if moment[1] not in done:
                        for player in moment[5]:
                            if player[1] not in output:
                                output[player[1]] = []
                            output[player[1]].append({
                                "x": player[2],
                                "y": player[3],
                                "game_clock": moment[2],
                                "shot_clock": moment[3]
                            })
                        done.append(moment[1])
                in_a_row = 0
            except Exception:
                in_a_row += 1
                print "Error: " + str(game_id) + "/" + str(current_event)
            finally:
                if in_a_row == 25:
                    in_a_row = 0
                    current_event = 1
                    break
                current_event += 1
        yield game_id, output

