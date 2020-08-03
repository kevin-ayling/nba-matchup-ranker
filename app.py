from flask import Flask
from nba.utils import get_games_str
from nba.games import find_games_info
from nba.aws import write_sns

app = Flask(__name__)


@app.route('/ping')
def hello():
    return "healthy"


@app.route('/date/<date>')
def date(date):
    games = find_games_info(date)
    games_str = get_games_str(games, date)
    write_sns(games_str)
    return games_str

if __name__ == '__main__':
    app.run()