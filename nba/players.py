from nba.static import league_leader_categories, find_league_leaders, find_rookie_league_leaders


stored_leaders = {}
stored_rookies = {}


# input: player_id - number, player_name - string
# output:
# leader =
#   {
#     'id': player_id,
#     'name': player_name,
#     'stat': category,
#     'rank': rank
#   }
def find_player_league_leader_info(player_id, season):
    if season in stored_leaders:
        league_leaders = stored_leaders[season]
    else:
        league_leaders = find_league_leaders(season)
        stored_leaders[season] = league_leaders
    leader_info = []
    for category in league_leader_categories:
        if is_leader(league_leaders[category], player_id):
            leader_info.append(find_league_leader_info(category, league_leaders[category], player_id))
    return leader_info


def find_player_rookie_league_leader_info(player_id, season):
    if season in stored_rookies:
        rookie_leaders = stored_rookies[season]
    else:
        rookie_leaders = find_rookie_league_leaders(season)
        stored_rookies[season] = rookie_leaders
    leader_info = []
    for category in league_leader_categories:
        if is_leader(rookie_leaders[category], player_id):
            leader_info.append(find_league_leader_info(category, rookie_leaders[category], player_id))
    return leader_info


def is_leader(player_list, player_id):
    for player in player_list:
        if player['PLAYERID'] == player_id:
            return True
    return False


exciting_categories = ['Points', 'Playmaking', 'Efficiency', 'Fast Break', 'Scoring Breakdown']
important_categories = ['Assists', 'Clutch']
bygone_era_categories = ['Rebounds', 'Defense']


def find_league_leader_info(category, player_list, player_id, rookie=False):
    multiplier = 0
    if category in exciting_categories:
        multiplier = 1.0
    elif category in important_categories:
        multiplier = 0.5
    rank = 0
    for player in player_list:
        rank += 1
        if player['PLAYERID'] == player_id:
            score = (multiplier * (5-rank)) + 1
            leader = {'id': player_id,
                      'name': player['PLAYER'],
                      'stat': category,
                      'rank': rank,
                      'score': score}
            return leader
