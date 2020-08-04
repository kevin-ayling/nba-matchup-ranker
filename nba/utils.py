from requests.exceptions import Timeout
from time import sleep
from datetime import datetime

league_leader_category_str = {'Points': 'Pts', 'Rebounds': 'Reb', 'Assists': 'Ast', 'Defense': 'Def',
                              'Clutch': 'Clutch', 'Playmaking': 'Playmaking', 'Efficiency': 'Eff',
                              'Fast Break': 'Fast Break', 'Scoring Breakdown': 'Scoring Breakdown'}


def call_nba_api(api_call, positional_arguments, keyword_arguments):
    failures = 1
    print('initiating call to {} with {}, {}'.format(api_call, positional_arguments, keyword_arguments))
    while True:
        try:
            resp = api_call(*positional_arguments, **keyword_arguments)
            return resp
        except Timeout as ex:
            if failures > 25:
                print("Caught {} {}s in a row from {}. Raising error and exiting.".format(failures, type(ex).__name__,
                                                                                          api_call))
                raise RuntimeError
            wait_time = failures * failures
            print(
                "Catching {} #{} from {}, sleeping for {} and proceeding".format(type(ex).__name__, failures, api_call,
                                                                                 '{}s'.format(wait_time)))
            sleep(wait_time)
            failures += 1
        except Exception as ex:
            print("Caught {} from {} with args: {}, {}".format(type(ex).__name__, api_call, positional_arguments,
                                                               keyword_arguments))
            print(ex)
            raise RuntimeError


def find_matchup(game_id, matchups):
    for matchup in matchups:
        if matchup['id'] == game_id:
            return matchup
    return None


def find_season(date):
    year = date.year
    if date.month > 8:
        year2 = int(date.strftime('%y')) + 1
        return '{}-{}'.format(year, year2)
    else:
        year2 = date.strftime('%y')
        return '{}-{}'.format(year - 1, year2)


def print_games(matchups, date):
    print('------------------------------------------------------------------------')
    print('{} NBA Games on {}, {} {} {}'.format(len(matchups), date.strftime('%A'), date.strftime("%B"), date.day,
                                                date.year))
    print('------------------------------------------------------------------------')
    print('')
    print('------------------------------------------------------------------------')
    i = 1
    for matchup in matchups:
        print('{}. {} vs. {}'.format(i, matchup['teams'][0]['name'], matchup['teams'][1]['name']))
        print_tv_info(matchup)
        print_result(matchup)
        print_league_leader_string(matchup)
        print_rookie_string(matchup)
        print('   Team Score: {}, Player Score: {}, Overall: {}'.format(matchup['score']['team'],
                                                                        matchup['score']['player'],
                                                                        matchup['score']['overall']))
        print('------------------------------------------------------------------------')
        i += 1


def get_games_str(matchups, user_date):
    # converted_date = datetime.strptime(user_date, '%m-%d-%y')
    converted_date = user_date
    games_str = '------------------------------------------------------------------------\n'
    games_str += '{} NBA Games on {}, {} {} {}\n'.format(len(matchups), converted_date.strftime('%A'),
                                                         converted_date.strftime("%B"), converted_date.day,
                                                         converted_date.year)
    games_str += '------------------------------------------------------------------------\n'
    games_str += '\n'
    games_str += '------------------------------------------------------------------------\n'
    i = 1
    for matchup in matchups:
        games_str += '{}. {} vs. {}\n'.format(i, matchup['teams'][0]['name'], matchup['teams'][1]['name'])
        games_str += get_tv_info(matchup)
        games_str += get_result(matchup)
        games_str += get_league_leader_string(matchup)
        games_str += get_rookie_string(matchup)
        games_str += '   Team Score: {}, Player Score: {}, Overall: {}\n'.format(matchup['score']['team'],
                                                                                 matchup['score']['player'],
                                                                                 matchup['score']['overall'])
        games_str += '------------------------------------------------------------------------\n'
        i += 1
    return games_str


def get_games_str_sns(matchups, user_date):
    # converted_date = datetime.strptime(user_date, '%m-%d-%y')
    converted_date = user_date
    games_str = '-------------------------\n'
    games_str += '{} NBA Games on {}, {} {} {}\n'.format(len(matchups), converted_date.strftime('%A'),
                                                         converted_date.strftime("%B"), converted_date.day,
                                                         converted_date.year)
    games_str += '-------------------------\n'
    games_str += '\n'
    games_str += '-------------------------\n'
    i = 1
    for matchup in matchups:
        games_str += '{}. {} vs. {}\n'.format(i, matchup['teams'][0]['name'], matchup['teams'][1]['name'])
        games_str += get_tv_info_sns(matchup)
        games_str += get_league_leader_string(matchup)
        games_str += get_rookie_string(matchup)
        games_str += '-------------------------\n'
        i += 1
    return games_str


def print_league_leader_string(matchup):
    if len(matchup['leagueleaders']) == 0:
        return
    print('   League Leaders:')
    leaders = []
    league_leader_str = ''
    previous_leader = 0
    for leader in matchup['leagueleaders']:
        leaders.append(leader['id'])
        if leader['id'] == previous_leader:
            league_leader_str += ', {}({})'.format(league_leader_category_str[leader['stat']], leader['rank'])
        elif len(league_leader_str) == 0:
            league_leader_str += '   {} - {}({})'.format(leader['name'], league_leader_category_str[leader['stat']], leader['rank'])
            previous_leader = leader['id']
        else:
            print(league_leader_str)
            league_leader_str = '   {} - {}({})'.format(leader['name'], league_leader_category_str[leader['stat']], leader['rank'])
            previous_leader = leader['id']
    print(league_leader_str)
    for allstar in matchup['allstars']:
        if allstar['id'] in leaders: pass
        else: print('   {} - All Star'.format(allstar['name']))



def print_rookie_string(matchup):
    if len(matchup['rookies']) == 0:
        return
    print('   Rookies:')
    league_leader_str = ''
    previous_leader = 0
    for leader in matchup['rookies']:
        # print('   {} - {}({})'.format(leader['name'], leader['stat'], leader['rank']))
        if leader['id'] == previous_leader:
            league_leader_str += ', {}({})'.format(league_leader_category_str[leader['stat']], leader['rank'])
        elif len(league_leader_str) == 0:
            league_leader_str += '   {}(R) - {}({})'.format(leader['name'], league_leader_category_str[leader['stat']], leader['rank'])
            previous_leader = leader['id']
        else:
            print(league_leader_str)
            league_leader_str = '   {}(R) - {}({})'.format(leader['name'], league_leader_category_str[leader['stat']], leader['rank'])
            previous_leader = leader['id']
    print(league_leader_str)


def get_league_leader_string(matchup):
    if len(matchup['leagueleaders']) == 0:
        return ''
    league_leader_str = ''
    local_league_leader_str = ''
    previous_leader = 0
    leaders = []
    for leader in matchup['leagueleaders']:
        leaders.append(leader['id'])
        if leader['id'] == previous_leader:
            local_league_leader_str += ', {}({})'.format(league_leader_category_str[leader['stat']], leader['rank'])
        elif len(local_league_leader_str) == 0:
            local_league_leader_str += '   {} - {}({})'.format(leader['name'], league_leader_category_str[leader['stat']], leader['rank'])
            previous_leader = leader['id']
        else:
            league_leader_str += local_league_leader_str
            league_leader_str += '\n'
            local_league_leader_str = '   {} - {}({})'.format(leader['name'], league_leader_category_str[leader['stat']], leader['rank'])
            previous_leader = leader['id']
    league_leader_str += local_league_leader_str
    league_leader_str += '\n'
    for allstar in matchup['allstars']:
        if allstar['id'] in leaders: pass
        else:
            league_leader_str += '   {} - All Star'.format(allstar['name'])
            league_leader_str += '\n'
    return league_leader_str


def get_rookie_string(matchup):
    if len(matchup['rookies']) == 0:
        return ''
    league_leader_str = ''
    local_league_leader_str = ''
    previous_leader = 0
    for leader in matchup['rookies']:
        # print('   {} - {}({})'.format(leader['name'], leader['stat'], leader['rank']))
        if leader['id'] == previous_leader:
            local_league_leader_str += ', {}({})'.format(league_leader_category_str[leader['stat']], leader['rank'])
        elif len(local_league_leader_str) == 0:
            local_league_leader_str += '   {}(R) - {}({})'.format(leader['name'], league_leader_category_str[leader['stat']], leader['rank'])
            previous_leader = leader['id']
        else:
            league_leader_str += local_league_leader_str
            league_leader_str += '\n'
            local_league_leader_str = '   {}(R) - {}({})'.format(leader['name'], league_leader_category_str[leader['stat']], leader['rank'])
            previous_leader = leader['id']
    league_leader_str += local_league_leader_str
    league_leader_str += '\n'
    return league_leader_str


def print_tv_info(matchup):
    if len(matchup['tv']) == 0:
        return
    elif matchup['tv']['scope'] == 'National':
        print('   {} on {} from the {}'.format(matchup['time'], matchup['tv']['network'], matchup['venue']))
    else:
        print('   {} on {} ({}) from the {}'.format(matchup['time'], matchup['tv']['network'], matchup['tv']['scope'],
                                                    matchup['venue']))


def get_tv_info(matchup):
    if len(matchup['tv']) == 0:
        return ''
    elif matchup['tv']['scope'] == 'National':
        return '   {} on {} from the {}\n'.format(matchup['time'], matchup['tv']['network'], matchup['venue'])
    else:
        return '   {} on {} ({}) from the {}\n'.format(matchup['time'], matchup['tv']['network'],
                                                       matchup['tv']['scope'],
                                                       matchup['venue'])


def get_tv_info_sns(matchup):
    if len(matchup['tv']) == 0:
        return ''
    elif matchup['tv']['scope'] == 'National':
        return '   {} on {}\n'.format(matchup['time'], matchup['tv']['network'])
    else:
        return '   {} on {} ({})\n'.format(matchup['time'], matchup['tv']['network'],
                                           matchup['tv']['scope'])


def print_result(matchup):
    if matchup['outcome']['w_score'] == 0:
        return
    else:
        winner = ''
        loser = ''
        for team in matchup['teams']:
            if matchup['outcome']['winner'] == team['id']:
                winner = team['name']
            elif matchup['outcome']['loser'] == team['id']:
                loser = team['name']
        print(
            '   {} def {} {} - {}'.format(winner, loser, matchup['outcome']['w_score'], matchup['outcome']['l_score']))


def get_result(matchup):
    if matchup['outcome']['w_score'] == 0:
        return ''
    else:
        winner = ''
        loser = ''
        for team in matchup['teams']:
            if matchup['outcome']['winner'] == team['id']:
                winner = team['name']
            elif matchup['outcome']['loser'] == team['id']:
                loser = team['name']
        return '   {} def {} {} - {}\n'.format(winner, loser, matchup['outcome']['w_score'],
                                               matchup['outcome']['l_score'])
