import requests
import json
from psycopg2.extras import Json
import datetime

# def merge_two_dicts(x, y):
#     '''Given two dicts, merge them into a new dict as a shallow copy.'''
#     z = x.copy()
#     z.update(y)
#     return z

def get_teams():

    with open('teams.json', 'r') as fp:
        teams = json.load(fp)

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
                "conference-rank": table[11]
            }

    with open('teams.json', 'w') as outfile:
        json.dump(teams, outfile, sort_keys=True, indent=4, separators=(',', ': '))

    return teams

get_teams()

def get_games():

    with open('games.json', 'r') as fp:
        games = json.load(fp)

    game_ids = []
    url = "http://stats.nba.com/stats/leaguegamelog?Counter=1000&Direction=DESC&LeagueID=00&PlayerOrTeam=T&" \
          "Season=2015-16&SeasonType=Regular+Season&Sorter=PTS"
    response = requests.get(url)
    table = response.json()["resultSets"][0]["rowSet"]

    for row in table:
        game_ids.append(str(row[4]))

    for index, game_id in enumerate(game_ids):
        if game_id not in games.keys():
            url = "http://stats.nba.com/stats/boxscoresummaryv2?GameID="+str(game_id)
            try:
                response = requests.get(url)
                table = response.json()["resultSets"]
                game_info = table[4]["rowSet"][0]
                game_scores = table[5]["rowSet"]
                stats_available = table[8]["rowSet"][0][2] + table[8]["rowSet"][0][3]
                if stats_available == 2:
                    games[game_id] = {
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
            print index

    with open('games.json', 'w') as outfile:
        json.dump(games, outfile, sort_keys=True, indent=4, separators=(',', ': '))

    return games


def get_movement(completed_games):
    with open('games.json', 'r') as fp:
        game_ids = json.load(fp).keys()



    for game_id in game_ids:
        if game_id not in completed_games:
            current_event = 1
            in_a_row = 0
            movement = {}
            header = False
            while True:
                url = "http://stats.nba.com/stats/locations_getmoments/?eventid="+str(current_event)+"&gameid="+game_id
                try:
                    response = requests.get(url)
                    moments = response.json()["moments"]
                    if not header:
                        movement["away_team"] = response.json()["visitor"]
                        movement["home_team"] = response.json()["home"]
                        movement["movement"] = {}
                        header = True
                    in_a_row = 0
                    for moment in moments:
                        # For each player/ball in the list found within each moment
                        for player in moment[5]:
                            if player[1] in movement["movement"].keys():
                                movement["movement"][player[1]]["rows"].append(
                                    [moments.index(moment), moment[1], player[2], player[3], moment[2], moment[3]]
                                )
                            else:
                                movement["movement"][player[1]] = {
                                    "header": ["index", "timestamp", "x", "y", "game_clock", "shot_clock"],
                                    "rows": [
                                        [moments.index(moment), moment[1], player[2], player[3], moment[2], moment[3]]
                                    ]
                                }
                except ValueError:
                    in_a_row += 1
                    if in_a_row == 20:
                        break
                    print "No Events Available: " + str(game_id) + "/" + str(current_event)
                except KeyError:
                    in_a_row += 1
                    if in_a_row == 20:
                        break
                    print "No Events Available: " + str(game_id) + "/" + str(current_event)
                finally:
                    current_event += 1
            yield (game_id, Json(movement["home_team"]), Json(movement["away_team"]), Json(movement["movement"]))
        else:
            print "Skipping game id " + str(game_id)

