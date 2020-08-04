from nba.utils import find_matchup, find_season
from nba.teams import find_team_league_leader_info, find_team_playoff_ranking, find_team_name, find_team_rookie_info, find_team_allstars
from nba.tv import find_tv_info, find_tv_year
from datetime import date, timedelta, datetime
from nba.static import find_static_games, find_scoreboard, find_common_team_info, find_all_stars


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
    matchup['allstars'].extend(find_team_allstars(team_id, season))
    matchup['leagueleaders'].extend(find_team_league_leader_info(team_id, season))
    matchup['rookies'].extend(find_team_rookie_info(team_id, season))


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
               'allstars': [],
               'leagueleaders': [],
               'rookies': [],
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
# output: rank - number (0-26)
# rank = 30 - (team1_rank + team2_rank)
def find_matchup_team_score(matchup, season):
    team_ranks = 0
    for team in matchup['teams']:
        team_rank = find_team_playoff_ranking(team['id'], season) * 2
        if team_rank > 20:
            team_rank = 20
        team_ranks += team_rank
    score = 30 - team_ranks
    if score < 0:
        return 0
    return score


# input: matchup, season
# output: rank - number (0-25)
def find_matchup_player_score(matchup):
    league_leader_score = find_league_leader_score(matchup['leagueleaders'], matchup['allstars'])
    if matchup['teams'][0]['name']  == 'Pelicans' or matchup['teams'][1]['name']  == 'Pelicans':
        matchup['rookies'].append({'id': 0,
                      'name': 'Zion Williamson',
                      'stat': 'Points',
                      'rank': 1,
                      'score': 5})
    rookie_score = find_rookie_score(matchup['rookies']) / 2
    score = league_leader_score + rookie_score
    if score > 25: return 25
    return score


def find_rookie_score(leaders):
    score = 0
    players = {}
    for leader in leaders:
        if leader['id'] in players:
            newscore = players[leader['id']] + leader['score']
            if newscore > 8: newscore = 8
            players[leader['id']] = newscore
        if leader['name'] == 'Ja Morant' or leader['name'] == 'Zion Williamson':
            players[leader['id']] = 8
        else:
            players[leader['id']] = leader['score']
    for player in players:
        score += players[player]
    if score > 25:
        return 25
    return score


def find_league_leader_score(leaders, allstars):
    score = 0
    players = {}
    for leader in leaders:
        if leader['id'] in players:
            newscore = players[leader['id']] + leader['score']
            if newscore > 8: newscore = 8
            players[leader['id']] = newscore
        if leader['name'] == 'Ja Morant' or leader['name'] == 'Zion Williamson':
            players[leader['id']] = 8
        else:
            players[leader['id']] = leader['score']
    for allstar in allstars:
        if allstar['id'] in players:
            if players[allstar['id']] >= 5: players[allstar['id']] = 8
            else: players[allstar['id']] += 3
        else:
            score += 3
    for player in players:
        score += players[player]
    if score > 25:
        return 25
    return score

