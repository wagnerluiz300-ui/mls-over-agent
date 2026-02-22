from datetime import datetime

today = datetime.today().strftime('%Y-%m-%d')

querystring = {
    "league": LEAGUE_ID,
    "season": SEASON,
    "date": today
}
