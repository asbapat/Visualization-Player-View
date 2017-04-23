from flask import Flask
from flask import render_template

import numpy as np
import random
import json
import pandas as pd
import math

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
    for index, row in premier_league_data.loc[:, ['Player Surname','Time Played', 'Goals', 'Position Id']].iterrows():
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
        player_dict[surname].append({"name": "Position: " + position, "size": "Position: "})
        player_dict[surname].append({"name": "Time Played: " + str(row['Time Played']), "size": "Time Played: "})
        player_dict[surname].append({"name": "Goals: " + str(row['Goals']), "size": "Goals: "})


    i = 0
    team_list = list()
    for player in player_list:
        teams_dict[teams[i]].append({"name": player, "children": player_dict[player]})
        player_stats_list.append({"name": player, "children": player_dict[player]})
        i += 1

    for team in teams_dict:
        team_list.append({"name":team, "children": teams_dict[team]})

    league_dict = {"name": "English Premier League", "children": team_list}
    return league_dict


def find_best_k():
    no_of_cluster = range(1, 25)
    clusters_list = list()
    centroid_list = list()
    euclidean_distance_list = list()
    min_distance_list = list()
    average_squared_sum_list = list()
    elbow_list = list()


    # Create clusters with different k values
    for cluster in no_of_cluster:
        clusters_list.append(KMeans(n_clusters=cluster).fit(premier_league_data.values))

    # Find the centroid of each cluster
    for cluster in clusters_list:
        centroid_list.append(cluster.cluster_centers_)

    # Compute the distance between centroid of a cluster and each value
    for centroid in centroid_list:
        euclidean_distance_list.append(cdist(premier_league_data.values, centroid, 'euclidean'))

    # Find the minimum distance column wise for each distance in the euclidean_distance_list
    for distance in euclidean_distance_list:
        min_distance_list.append(np.min(distance, axis=1))

    # Calculate the average squared sum for each distance
    for dist in min_distance_list:
        average_squared_sum_list.append(sum(dist) / premier_league_data.values.shape[0])

    for cluster in no_of_cluster:
        elbow_dict = dict()
        elbow_dict[cluster] = {'K': cluster, 'AvgSS': average_squared_sum_list[cluster-1]}
        elbow_list.append(elbow_dict[cluster])

    return elbow_list


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


@app.route("/adaptivesampling")
def adaptivesampling():
    # Implement adaptive sampling
    # Find best value of k by elbow method
    elbow_values = find_best_k()
    with open(JSON_DIR + 'kmeans_json.json', 'w') as f:
        json.dump(elbow_values, f)

    # No. of clusters is obtained from find_best_k()
    no_of_clusters = 5
    adaptive_sample_of_players = adaptive_sampling(no_of_clusters)

    # Perform PCA on the sampled data based on best PCA attributes
    pca = PCA(n_components=5).fit(adaptive_sample_of_players)

    pca = pca.transform(adaptive_sample_of_players)

    sample_player_names = list()
    for value in adaptive_sample_of_players.index.values:
        sample_player_names.append(player_names[value])

    se = pd.DataFrame(sample_player_names)
    pca = np.concatenate((pca, se), axis=1)

    pca_values = pd.DataFrame(pca)
    pca_values.columns = ['PCA1', 'PCA2', 'PCA3', 'PCA4', 'PCA5', 'Name']
    json_values = pca_values.to_json(orient='records')

    with open(JSON_DIR + 'pca_values_adaptive_json.json', 'w') as f:
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

    league_list = make_collapsible_tree()
    
    with open(JSON_DIR +'league.json', 'w') as f:
            json.dump(league_list, f)
    
    player_names = list(premier_league_data.index.values)
    premier_league_data.index.names = ['Player Name']
    premier_league_data.columns.names = ['Attributes']
    del premier_league_data['Team']
    del premier_league_data['Position Id']
    premier_league_data = premier_league_data.set_index(['Player Surname'])
    scaler = MinMaxScaler()
    premier_league_data = pd.DataFrame(scaler.fit_transform(premier_league_data), columns=premier_league_data.columns)

    app.run(host='0.0.0.0', port=8086, debug=True, use_reloader=False)
