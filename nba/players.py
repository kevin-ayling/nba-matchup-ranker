from nba.static import league_leader_categories, find_league_leaders


stored_leaders = {}

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


def is_leader(player_list, player_id):
    for player in player_list:
        if player['PLAYERID'] == player_id:
            return True
    return False


def find_league_leader_info(category, player_list, player_id):
    rank = 0
    for player in player_list:
        rank +=1
        if player['PLAYERID'] == player_id:
            leader =  {'id': player_id,
                             'name': player['PLAYER'],
                             'stat': category,
                             'rank': rank}
            return leader
