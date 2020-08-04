from nba.players import find_player_league_leader_info, find_player_rookie_league_leader_info
from nba.static import find_teams, find_standings, find_all_stars

stored_teams = {}
stored_standings = {}
stored_allstars = {}


def find_team_name(team_id, season):
    if season in stored_standings:
        standings = stored_standings[season]
    else:
        standings = find_standings(season)
        stored_standings[season] = standings
    for team in standings['Standings']:
        if team['TeamID'] == team_id:
            return team['TeamName']


# input: teamId - number
# output: playoffRank - number (1-15)
def find_team_playoff_ranking(team_id, season):
    if season in stored_standings:
        standings = stored_standings[season]
    else:
        standings = find_standings(season)
        stored_standings[season] = standings
    for team in standings['Standings']:
        if team['TeamID'] == team_id:
            return team['PlayoffRank']


# input: teamId - number
# output:
# leaders =
#   [{
#     'id': player_id,
#     'name': player_name,
#     'stat': category,
#     'rank': rank
#   }]
def find_team_league_leader_info(team_id, season):
    if season in stored_teams:
        teams = stored_teams[season]
    else:
        teams = find_teams(season)
        stored_teams[season] = teams
    leaders = []
    if isinstance(team_id, int):
        if team_id in teams:
            pass
        else:
            team_id = str(team_id)
    for player in teams[team_id]:
        leaders.extend(find_player_league_leader_info(player['PLAYER_ID'], season))
    return leaders


def find_team_rookie_info(team_id, season):
    if season in stored_teams:
        teams = stored_teams[season]
    else:
        teams = find_teams(season)
        stored_teams[season] = teams
    leaders = []
    if isinstance(team_id, int):
        if team_id in teams:
            pass
        else:
            team_id = str(team_id)
    for player in teams[team_id]:
        leaders.extend(find_player_rookie_league_leader_info(player['PLAYER_ID'], season))
    return leaders


def find_team_allstars(team_id, season):
    if season in stored_teams:
        teams = stored_teams[season]
    else:
        teams = find_teams(season)
        stored_teams[season] = teams
    allstars = []
    if isinstance(team_id, int):
        if team_id in teams:
            pass
        else:
            team_id = str(team_id)
    for player in teams[team_id]:
        if is_allstar(player['PLAYER_ID'], season):
            allstars.append({'id': player['PLAYER_ID'], 'name': player['PLAYER']})
        else:
            pass
    return allstars


def is_allstar(player_id, season):
    if season in stored_allstars:
        allstars = stored_allstars[season]
    else:
        allstars = find_all_stars(season)
        stored_allstars[season] = allstars
    for allstar in allstars['LeagueGameLog']:
        if player_id == allstar['PLAYER_ID']:
            return True
    return False
