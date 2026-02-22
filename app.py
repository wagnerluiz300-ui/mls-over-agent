import requests
import numpy as np
from scipy.stats import poisson
from flask import Flask, jsonify
import os

app = Flask(__name__)

API_KEY = os.environ.get("API_KEY")

LEAGUE_ID = 253
SEASON = 2025
LEAGUE_AVG = 3.0

def calculate_over25(home_scored, home_conceded,
                     away_scored, away_conceded,
                     odd):

    attack_home = home_scored / (LEAGUE_AVG / 2)
    defense_away = away_conceded / (LEAGUE_AVG / 2)

    attack_away = away_scored / (LEAGUE_AVG / 2)
    defense_home = home_conceded / (LEAGUE_AVG / 2)

    lambda_home = attack_home * defense_away * (LEAGUE_AVG / 2)
    lambda_away = attack_away * defense_home * (LEAGUE_AVG / 2)

    lambda_total = lambda_home + lambda_away

    adjustment = 0
    if home_scored > 1.5 and away_scored > 1.5:
        adjustment += 0.06
    if home_conceded > 1.5 and away_conceded > 1.5:
        adjustment += 0.04

    lambda_final = lambda_total * (1 + adjustment)

    prob_under3 = (
        poisson.pmf(0, lambda_final) +
        poisson.pmf(1, lambda_final) +
        poisson.pmf(2, lambda_final)
    )

    prob_over = 1 - prob_under3
    ev = (prob_over * odd) - 1

    if prob_over >= 0.58 and ev >= 0.05 and lambda_final >= 2.95:
        status = "APROVADA"
    else:
        status = "DESCARTAR"

    return {
        "lambda": round(lambda_final, 2),
        "prob_over_%": round(prob_over * 100, 2),
        "ev_%": round(ev * 100, 2),
        "status": status
    }

@app.route("/")
def run_agent():

    if not API_KEY:
        return jsonify({"erro": "API_KEY não configurada."})

    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"

    querystring = {
        "league": LEAGUE_ID,
        "season": SEASON,
        "next": 5
    }

    headers = {
        "X-RapidAPI-Key": API_KEY
    }

    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()

    results = []

    for match in data.get("response", []):
        home = match["teams"]["home"]["name"]
        away = match["teams"]["away"]["name"]

        home_scored = 1.7
        home_conceded = 1.5
        away_scored = 1.6
        away_conceded = 1.6

        odd = 1.70

        analysis = calculate_over25(
            home_scored,
            home_conceded,
            away_scored,
            away_conceded,
            odd
        )

        results.append({
            "match": f"{home} x {away}",
            **analysis
        })

    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
