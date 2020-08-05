from nba.utils import get_games_str, get_games_str_sns, print_games
from nba.static import find_links
from nba.games import find_games_info
from datetime import datetime
from nba.aws import write_sns, invoke_lambda
from nba.links import map_links, generate_html_and_write_to_s3, print_links



def date_handler(event, context):
    if 'date' in event:
        user_date = datetime.strptime(event['date'], '%m/%d/%y')
        games = find_games_info(user_date)
        return games
    else:
        today = datetime.today()
        games = find_games_info(today)
        games_str = get_games_str_sns(games, today)
        links = find_links(today)
        generate_html_and_write_to_s3(map_links(games, links))
        write_sns(games_str)
    return


if __name__ == "__main__":
    x = date_handler({'date': '08/04/20'}, {})
    # x = date_handler({}, {})

    print(x)