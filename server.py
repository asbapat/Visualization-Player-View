from flask import Flask
from flask import render_template

import numpy as np
import random
import json
import pandas as pd

from scipy.spatial.distance import cdist
from sklearn.preprocessing import normalize, MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn import metrics
from sklearn.manifold import MDS

JSON_DIR = 'static/leaguejson/'


def make_collapsible_tree():
    teams = list()                  # Stores the club of each player
    club_list = list()              # Stores the unique list of clubs
    player_stats_list = list()      # Stores the statistics of each player
    player_list = list()            # Stores the surname of each player
    stats_list = list()             # Stores the stats of each player
    teams_dict = dict()             # Maps the player to his particular club
    player_dict = dict()            # Maps the statistics to a player

    for team in premier_league_data.loc[:, "Team"]:
        teams.append(team)
        if team not in club_list:
            club_list.append(team)
            teams_dict[team] = []

    unique_id = 1
    i = 0
    for index, row in premier_league_data.loc[:, ['Player Surname','Time Played', 'Goals', 'Position Id', 'Big Chances', 'Total Fouls Conceded']].iterrows():
        surname = row['Player Surname']
        position_id = int(row['Position Id'])
        # If two players have the same surname
        if surname in player_dict:
            surname += str(unique_id)
            unique_id += 1

        if position_id == 1:
            position = 'Goalkeeper'
        elif position_id == 2:
            position = 'Defender'
        elif position_id == 4:
            position = 'Midfielder'
        elif position_id == 6:
            position = 'Striker'

        player_list.append(surname)
        player_dict[surname] = []
        stats_dict = {"Position": position, "Time Played": row['Time Played'], "Goals": row['Goals']}
        stats_list.append([stats_dict])
        team_logo = 'static/lib/images/logos/' + teams[i] + '.png'
        i += 1
        # player_dict[surname].append({"name": "Position: " + position, "size": "Position: "})
        # player_dict[surname].append({"name": "Time Played: " + str(row['Time Played']), "size": "Time Played: "})
        # player_dict[surname].append({"name": "Goals: " + str(row['Goals']), "size": "Goals: "})
        player_dict[surname].append(position)
        player_dict[surname].append(row['Time Played'])
        player_dict[surname].append(row['Goals'])
        player_dict[surname].append(team_logo)
        player_dict[surname].append(row['Big Chances'])
        player_dict[surname].append(row['Total Fouls Conceded'])

    i = 0
    team_list = list()
    for player in player_list:
        team_jersey = 'static/lib/images/jerseys/' + teams[i] + '.png'
        player_image = 'static/lib/images/players/' + player + '.png'
        teams_dict[teams[i]].append({"name": player, "jersey_image": team_jersey, "player_image": player_image,
                                     "position": player_dict[player][0], "time_played": player_dict[player][1],
                                     "goals": player_dict[player][2], "player_logo": player_dict[player][3],
                                     "bigchances": player_dict[player][4], "totalFouls": player_dict[player][5]})
        # player_stats_list.append({"name": player, "children": player_dict[player]})
        i += 1

    for team in teams_dict:
        team_logo = 'static/lib/images/logos/' + team + '.png'
        team_list.append({"name":team, "image": team_logo, "children": teams_dict[team]})

    premier_league_logo = 'static/lib/images/logos/Pl_logo.png'
    league_dict = {"name": "English Premier League", "image": premier_league_logo, "children": team_list}
    return league_dict


def calculate_bps():
    bps_score_dict = dict()

    unique_id = 1
    for index, row in gameweek_premier_league_data.loc[:, ['Player Surname', 'Time Played', 'Goals', 'Position Id']].iterrows():
        surname = row['Player Surname']
        # If two players have the same surname
        if surname in bps_score_dict:
            surname += str(unique_id)
            unique_id += 1

        bps_score = 0
        if int(row['Time Played']) > 0 and int(row['Time Played']) < 60:
            bps_score += 3
        elif int(row['Time Played']) > 60:
            bps_score += 6
        bps_score_dict[row['Player Surname']] = bps_score

    return bps_score_dict


def adaptive_sampling(no_of_clusters):
    cluster_features = list()
    sample_percent = 0.5

    # Perform K-Means Clustering
    clusters = KMeans(n_clusters=no_of_clusters).fit(premier_league_data)

    # Add a column called 'cluster_no' in the data frame
    premier_league_data['cluster_no'] = clusters.labels_

    for i in range(no_of_clusters):
        # Get the number of samples in that particular cluster based on the sample percent
        samples_required = len(premier_league_data[premier_league_data['cluster_no'] == i]) * sample_percent
        # Find the samples(rows) that are a part of the i'th cluster. Run for all the features in a cluster
        data_from_cluster = premier_league_data[premier_league_data['cluster_no'] == i]
        # Get a random sample of the players from a particular cluster
        cluster_features.append(premier_league_data.ix[random.sample(data_from_cluster.index, int(samples_required))])

    # Combine the data for a particular player from all the features (columns) selected
    adaptive_sample_data = pd.concat(cluster_features)

    # Delete column 'cluster_no' from the data frame
    del adaptive_sample_data['cluster_no']

    return adaptive_sample_data


app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/pca")
def perform_pca():
    # Perform PCA on the data based on best PCA attributes
    pca = PCA(n_components=5).fit(premier_league_data)

    pca = pca.transform(premier_league_data)

    sample_player_names = list()
    for value in premier_league_data.index.values:
        sample_player_names.append(player_names[value])

    se = pd.DataFrame(player_names)
    pca = np.concatenate((pca, se), axis=1)

    pca_values = pd.DataFrame(pca)
    pca_values.columns = ['PCA1', 'PCA2', 'PCA3', 'PCA4', 'PCA5', 'Name']
    json_values = pca_values.to_json(orient='records')

    with open(JSON_DIR + 'players_pca_json.json', 'w') as f:
        f.write(json_values)

    return ('', 204)


if __name__ == "__main__":
    premier_league_data = pd.read_csv("Premier League 2011-12.csv", header=0,
                                      usecols=['Player Surname', 'Team', 'Time Played', 'Position Id', 'Goals', 'Assists', 'Clean Sheets',
                                             'Saves from Penalty', 'Saves Made', 'Yellow Cards', 'Red Cards',
                                             'Successful Dribbles', 'Shots Off Target inc woodwork',
                                             'Shots On Target inc goals', 'Key Passes', 'Big Chances',
                                             'Successful crosses in the air', 'Total Clearances', 'Blocks',
                                             'Interceptions', 'Recoveries', 'Tackles Won', 'Winning Goal',
                                             'Total Successful Passes All', 'Penalties Conceded',
                                             'Error leading to Goal', 'Error leading to Attempt',
                                             'Tackles Lost', 'Total Fouls Conceded', 'Offsides'])

    gameweek_premier_league_data = pd.read_csv("Premier League 2011-12 Gameweek.csv", header=0,
                                      usecols=['Player Surname', 'Team', 'Gameweek', 'Time Played', 'Position Id', 'Goals',
                                               'Assists', 'Clean Sheets',
                                               'Saves from Penalty', 'Saves Made', 'Yellow Cards', 'Red Cards',
                                               'Successful Dribbles', 'Shots Off Target inc woodwork',
                                               'Shots On Target inc goals', 'Key Passes', 'Big Chances',
                                               'Successful crosses in the air', 'Total Clearances', 'Blocks',
                                               'Interceptions', 'Recoveries', 'Tackles Won', 'Winning Goal',
                                               'Total Successful Passes All', 'Penalties Conceded',
                                               'Error leading to Goal', 'Error leading to Attempt',
                                               'Tackles Lost', 'Total Fouls Conceded', 'Offsides'])

    league_dict = make_collapsible_tree()
    
    with open(JSON_DIR +'league.json', 'w') as f:
            json.dump(league_dict, f)

    del premier_league_data['Team']
    del premier_league_data['Position Id']
    premier_league_data = premier_league_data.set_index(['Player Surname'])
    player_names = list(premier_league_data.index.values)
    premier_league_data.index.names = ['Player Name']
    premier_league_data.columns.names = ['Attributes']

    bps_score_values = calculate_bps()
    with open(JSON_DIR +'bps.json', 'w') as f:
            json.dump(bps_score_values, f)

    del gameweek_premier_league_data['Team']
    del gameweek_premier_league_data['Gameweek']
    del gameweek_premier_league_data['Position Id']
    gameweek_premier_league_data = gameweek_premier_league_data.set_index(['Player Surname'])
    gameweek_player_names = list(gameweek_premier_league_data.index.values)
    gameweek_premier_league_data.index.names = ['Player Name']
    gameweek_premier_league_data.columns.names = ['Attributes']


    scaler = MinMaxScaler()
    premier_league_data = pd.DataFrame(scaler.fit_transform(premier_league_data), columns=premier_league_data.columns)
    gameweek_premier_league_data = pd.DataFrame(scaler.fit_transform(gameweek_premier_league_data),
                                                columns=gameweek_premier_league_data.columns)

    app.run(host='0.0.0.0', port=8086, debug=True, use_reloader=False)
