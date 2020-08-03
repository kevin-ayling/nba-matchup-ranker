from nba.utils import find_matchup, find_season
from nba.teams import find_team_league_leader_info, find_team_playoff_ranking, find_team_name
from nba.tv import find_tv_info, find_tv_year
from datetime import date, timedelta, datetime
from nba.static import find_static_games, find_scoreboard, find_common_team_info


# input: offset - number of days after today
# output:
# matchups =
#   {[
#       id: id,
#       teams: [ id: id, teamName: name ]
#   ]}
def find_games_info(user_date):
    # converted_date = datetime.strptime(user_date, '%m-%d-%y')
    converted_date = user_date
    if datetime.today() - timedelta(days=1) <= converted_date:
        return find_future_matchups(converted_date)
    else:
        return find_previous_matchups(converted_date)


def find_future_matchups(date):
    matchups = []
    season = find_season(date)
    for team in find_team_list(date):
        matchup = find_matchup(str(team['gameId']), matchups)
        if matchup is None:
            matchup = create_matchup(team['gameId'], date)
            matchups.append(matchup)
        add_team_info(matchup, team, team['id'], find_team_name(team['id'], season), season)
    add_matchup_info(matchups, date, season)
    return matchups


def find_previous_matchups(date):
    matchups = []
    season = find_season(date)
    game_finder_results = find_static_games(date)
    for team in game_finder_results['LeagueGameFinderResults']:
        matchup = find_matchup(str(team['GAME_ID']), matchups)
        if matchup is None:
            matchup = create_matchup(team['GAME_ID'], date)
            matchups.append(matchup)
        add_team_info(matchup, team, team['TEAM_ID'], team['TEAM_NAME'], season)
    add_matchup_info(matchups, date, season)
    return matchups


def add_team_info(matchup, team, team_id, team_name, season):
    find_outcome(team, matchup)
    matchup['teams'].append({'id': team_id, 'name': team_name})
    matchup['leagueleaders'].extend(find_team_league_leader_info(team_id, season))


def add_matchup_info(matchups, date, season):
    find_tv_info(matchups, date)
    find_matchup_scores(matchups, season)
    matchups.sort(key=matchup_sort_key, reverse=True)


def find_team_list(date):
    scoreboard = find_scoreboard(date)
    teams = []
    for game in scoreboard['GameHeader']:
        winner = {'id': game['HOME_TEAM_ID'], 'gameId': game['GAME_ID']}
        loser = {'id': game['VISITOR_TEAM_ID'], 'gameId': game['GAME_ID']}
        teams.append(winner)
        teams.append(loser)
    return teams


def create_matchup(game_id, date):
    matchup = {'id': game_id,
               'teams': [],
               'score': {},
               'leagueleaders': [],
               'date': date.strftime('%m/%d/%Y'),
               'time': None,
               'venue': '',
               'tv': {},
               'outcome': {'winner': '',
                           'loser': '',
                           'w_score': 0,
                           'l_score': 0
                           }}
    return matchup


def matchup_sort_key(matchup):
    return matchup['score']['overall']


# input: team, matchup
# output: none
# sets WL info for team inside matchup['outcome']
def find_outcome(team, matchup):
    if 'WL' not in team:
        return
    else:
        if team['WL'] == 'W':
            matchup['outcome']['winner'] = team['TEAM_ID']
            matchup['outcome']['w_score'] = team['PTS']
        elif team['WL'] == 'L':
            matchup['outcome']['loser'] = team['TEAM_ID']
            matchup['outcome']['l_score'] = team['PTS']


# input:
# matchup =
#   {
#       id: id,
#       teams: [ id: id, teamName: name ]
#   ]
# output:
# score = {'overall': score,
#   'team': team_score,
#    'player': player_score }
def find_matchup_scores(matchups, season):
    for matchup in matchups:
        team_score = find_matchup_team_score(matchup, season)
        player_score = find_matchup_player_score(matchup)
        matchup['score'] = {'overall': team_score + player_score,
                            'team': team_score,
                            'player': player_score}


# input: matchup, season
# output: rank - number (0-28)
# rank = 30 - (team1_rank + team2_rank)
def find_matchup_team_score(matchup, season):
    team_ranks = 0
    for team in matchup['teams']:
        team_rank = find_team_playoff_ranking(team['id'], season)
        team_ranks += team_rank
    return 30 - team_ranks


# input: matchup, season
# output: rank - number (1-25)
def find_matchup_player_score(matchup):
    score = 1
    for leader in matchup['leagueleaders']:
        score = (score * (7 - leader['rank'])) / 2
    if score > 25:
        return 25
    return score
