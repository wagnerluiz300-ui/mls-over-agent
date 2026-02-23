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

    return round(prob_over_25, 3), round(implied_prob, 3), round(value, 3)

@app.route("/")
def get_games():

    if not API_KEY:
        return jsonify({"erro": "API_KEY não configurada no Railway"})

    url = "https://v3.football.api-sports.io/fixtures"

    headers = {
        "x-apisports-key": API_KEY
    }

    params = {
        "league": LEAGUE_ID,
        "season": SEASON,
        "next": 5
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
    except Exception as e:
        return jsonify({"erro_requisicao": str(e)})

    # Proteção contra erro da API
    if "response" not in data:
        return jsonify({
            "erro_api": data
        })

    results = []

    for game in data["response"]:

        home = game["teams"]["home"]["name"]
        away = game["teams"]["away"]["name"]

        # valores médios fixos (modelo base)
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
            "prob_over_2_5": prob,
            "implied_probability": implied,
            "value": value,
            "recomendacao": "ENTRAR" if value > 0.05 else "EVITAR"
        })

    return jsonify(results)
