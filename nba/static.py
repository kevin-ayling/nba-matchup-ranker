from nba_api.stats.endpoints import leaguestandings, homepageleaders, commonteamroster, leaguegamefinder, scoreboardv2, \
    teaminfocommon, leagueleaders, leaguegamelog
from nba.utils import call_nba_api
from nba.aws import read_obj, key_exists_in_s3, write_obj
import json
import requests
from os import path

league_leader_categories = ['Points', 'Rebounds', 'Assists', 'Defense', 'Clutch', 'Playmaking', 'Efficiency',
                            'Fast Break', 'Scoring Breakdown']


def find_all_stars(season):
    return find_and_write_data(season, 'LeagueAllStars.json', leaguegamelog.LeagueGameLog, [],
                               {'counter': 0, 'direction': 'ASC', 'league_id': '00', 'player_or_team_abbreviation': 'P',
                                'season': season, 'season_type_all_star': 'All Star', 'sorter': 'PTS'})


# def find_stat_leaders(season):
#     args = {
#         "league_id": "00",
#         "per_mode48": "Totals",
#         "scope": "S",
#         "season": "2019-20",
#         "season_type_all_star": "Regular Season",
#         "stat_category_abbreviation": "PTS"
#     }
#     x = call_nba_api(leagueleaders.LeagueLeaders, [],
#                      args).get_normalized_dict()


def find_league_leaders(season):
    static_leaders = read_from_s3('HomePageLeaders.json')
    if season in static_leaders:
        return static_leaders[season]
    else:
        league_leaders = {}
        for category in league_leader_categories:
            league_leaders[category] = []
            leaders = call_nba_api(homepageleaders.HomePageLeaders,
                                   ['Season', '00', 'Player', 'All Players', season,
                                    'Regular Season',
                                    category], {}).get_normalized_dict()
            league_leaders[category] = leaders['HomePageLeaders']
            static_leaders[season] = league_leaders

        write_obj(static_leaders, 'HomePageLeaders.json'.format(season))
        return static_leaders[season]


def find_rookie_league_leaders(season):
    static_rookies = read_from_s3('HomePageRookieLeaders.json')
    if season in static_rookies:
        return static_rookies[season]
    else:
        league_leaders = {}
        for category in league_leader_categories:
            league_leaders[category] = []
            leaders = call_nba_api(homepageleaders.HomePageLeaders,
                                   ['Season', '00', 'Player', 'Rookies', season,
                                    'Regular Season',
                                    category], {}).get_normalized_dict()
            league_leaders[category] = leaders['HomePageLeaders']
            static_rookies[season] = league_leaders

        write_obj(static_rookies, 'HomePageRookieLeaders.json'.format(season))
        return static_rookies[season]


def find_standings(season):
    return find_and_write_data(season, 'LeagueStandings.json', leaguestandings.LeagueStandings,
                               ['00', season, 'Regular Season'],
                               {})


def find_teams(season):
    stored_teams = read_from_s3('LeagueTeams{}.json'.format(season))
    if len(stored_teams) > 0:
        return stored_teams
    else:
        league_teams = {}
        standings = find_standings(season)
        for team in standings:
            team_resp = call_nba_api(commonteamroster.CommonTeamRoster, [team['TeamID'], season],
                                     {}).get_normalized_dict()
            league_teams[team['TeamID']] = team_resp['CommonTeamRoster']
        write_obj(league_teams, 'LeagueTeams{}.json'.format(season))
        return league_teams


def find_scoreboard(date):
    return find_and_write_data(date.strftime('%m/%d/%Y'), 'LeagueScoreBoard.json', scoreboardv2.ScoreboardV2,
                               [0, date.strftime('%Y-%m-%d'), '00'],
                               {})


def find_static_games(date):
    return find_and_write_data(date.strftime('%m/%d/%Y'), 'LeagueGames.json', leaguegamefinder.LeagueGameFinder, [],
                               {"league_id_nullable": "00", "player_or_team_abbreviation": "T",
                                "date_from_nullable": date.strftime('%m/%d/%Y'),
                                "date_to_nullable": date.strftime('%m/%d/%Y')})


#
# def find_team_matchup_history(season, team_id):
#     teamgames = call_nba_api(teamgamelog.TeamGameLog, [], {'season': season, 'season_type_all_star': 'Regular Season', 'team_id': team_id, 'league_id_nullable': '00'}).get_normalized_dict()
#     allteamgames = call_nba_api(teamgamelogs.TeamGameLogs, [], {}).get_normalized_dict()
#     print("hi")


def find_common_team_info(season):
    static_team_info = read_from_s3('LeagueTeamInfo.json')
    if season in static_team_info:
        return static_team_info[season]
    else:
        standings = find_standings(season)
        team_info = {}
        for team in standings:
            team_info[team['TeamID']] = call_nba_api(teaminfocommon.TeamInfoCommon, [],
                                                     {'league_id': '00', 'team_id': team['TeamID'],
                                                      'season_type_nullable': 'Regular Season',
                                                      'season_nullable': season}).get_normalized_dict()
        static_team_info[season] = team_info

        write_obj(static_team_info, 'LeagueTeamInfo.json'.format(season))
        return static_team_info[season]


def find_tv_data(year):
    static_tv_info = read_from_s3('LeagueTVInfo.json')
    if str(year) in static_tv_info:
        return static_tv_info[str(year)]
    static_tv_info[year] = requests.get(
        'http://data.nba.com/data/10s/v2015/json/mobile_teams/nba/{}/league/00_full_schedule.json'.format(year)).json()
    write_obj(static_tv_info, 'LeagueTVInfo.json')
    return static_tv_info[year]


def read_from_s3(key):
    if key_exists_in_s3(key):
        s3_data = read_obj(key)
        return s3_data
    return {}


def find_and_write_data(season, key, api_call, positional_arguments, keyword_arguments):
    s3_data = read_from_s3(key)
    if season in s3_data:
        return s3_data[season]
    s3_data[season] = call_nba_api(api_call, positional_arguments,
                                   keyword_arguments).get_normalized_dict()
    write_obj(s3_data, key)
    return s3_data[season]
