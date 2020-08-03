from nba.utils import get_games_str, get_games_str_sns
from nba.games import find_games_info
from datetime import datetime
from nba.aws import write_sns


def date_handler(event, context):
    if 'date' in event:
        user_date = datetime.strptime(event['date'], '%m/%d/%y')
        games = find_games_info(user_date)
        games_str = get_games_str(games, user_date)
    else:
        today = datetime.today()
        games = find_games_info(today)
        games_str = get_games_str_sns(games, today)
        write_sns(games_str)
    return games_str



if __name__ == "__main__":
    x = date_handler({'date': '08/02/20'}, {})
    print(x)