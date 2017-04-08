from flask import Flask
from flask import render_template

import numpy as np
import random
import json
import pandas as pd


app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')


if __name__ == "__main__":
    premier_league_data = pd.read_csv("Premier League 2011-12.csv", header=0, index_col=0,
                                      usecols=['Player Surname', 'Time Played', 'Goals', 'Assists', 'Clean Sheets',
                                             'Saves from Penalty', 'Saves Made', 'Yellow Cards', 'Red Cards',
                                             'Successful Dribbles', 'Shots Off Target inc woodwork',
                                             'Shots On Target inc goals', 'Key Passes', 'Big Chances',
                                             'Successful crosses in the air', 'Total Clearances', 'Blocks',
                                             'Interceptions', 'Recoveries', 'Tackles Won', 'Winning Goal',
                                             'Total Successful Passes All', 'Penalties Conceded',
                                             'Error leading to Goal', 'Error leading to Attempt',
                                             'Tackles Lost', 'Total Fouls Conceded', 'Offsides'])

    player_names = list(premier_league_data.index.values)
    premier_league_data.index.names = ['Player Name']
    premier_league_data.columns.names = ['Attributes']
    scaler = MinMaxScaler()
    premier_league_data = pd.DataFrame(scaler.fit_transform(premier_league_data), columns=premier_league_data.columns)

    app.run(host='0.0.0.0', port=8086, debug=True, use_reloader=False)