import os
import requests
import numpy as np
from scipy.stats import poisson
from flask import Flask, jsonify

app = Flask(__name__)

API_KEY = os.environ.get("API_KEY")

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

    return {
        "prob_over_2_5": round(prob_over_25, 3),
        "implied_probability": round(implied_prob, 3),
        "value": round(value, 3)
    }

@app.route("/")
def home():
    analysis = calculate_over25(
        1.7, 1.5,
        1.6, 1.6,
        1.70
    )
    return jsonify(analysis)
