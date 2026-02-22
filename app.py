import os
import requests
from scipy.stats import poisson
from flask import Flask, jsonify

app = Flask(__name__)

API_KEY = os.environ.get("API_KEY")

LEAGUE_ID = 253
SEASON = 2025
LEAGUE_AVG = 3.0

def calculate_over25(home_scored, home_conceded,
                     away_scored, away_conceded, odd):

    attack_home = home_scored / (LEAGUE_AVG / 2)
    defense_away = away_conceded / (LEAGUE_AVG / 2)

    attack_away = away_scored / (LEAGUE_AVG / 2)
    defense_home = home_conceded / (LEAGUE_AVG / 2)

    lambda_home = attack_home * defense_away * (LEAGUE_AVG / 2)
    lambda_away = attack_away * defense_home * (LEAGUE_AVG / 2)

    lambda_total = lambda_home + lambda_away

    prob_under_3 = poisson.cdf(2, lambda_total)
    prob_over_25 = 1 - prob_under_3

    implied_prob = 1 / odd
    value = prob_over_25 - implied_prob

    return prob_over_25, implied_prob, value


@app.route("/")
def get_games():

    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"

    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }

    params = {
        "league": LEAGUE_ID,
        "season": SEASON,
        "next": 5
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    results = []

    for game in data["response"]:

        home = game["teams"]["home"]["name"]
        away = game["teams"]["away"]["name"]

        home_scored = 1.7
        home_conceded = 1.4
        away_scored = 1.5
        away_conceded = 1.6

        odd = 1.75

        prob, implied, value = calculate_over25(
            home_scored,
            home_conceded,
            away_scored,
            away_conceded,
            odd
        )

        results.append({
            "match": f"{home} x {away}",
            "prob_over_2_5": round(prob,3),
            "value": round(value,3)
        })

    return jsonify(results)
