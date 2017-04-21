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


def make_collapsible_tree():
    teams = list()
    club_list = list()
    club_players_list = list()
    player_stats_list = list()
    league_dict = dict()
    teams_dict = dict()
    player_dict = dict()
    for team in premier_league_data.loc[:, "Team"]:
        teams.append(team)
        if team not in club_list:
            club_list.append(team)
            teams_dict[team] = []
    
    i = 0
    for player in premier_league_data.loc[:, "Player Surname"]:
        player_dict = {"name": player, "stats": []}
        teams_dict[teams[i]].append(player_dict)
        i += 1

    for team in teams_dict:
        club_players_list.append({"name": team, "children": teams_dict[team]})
    league_dict = {"name": "English Premier League", "children": club_players_list}
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


if __name__ == "__main__":
    premier_league_data = pd.read_csv("Premier League 2011-12.csv", header=0,
                                      usecols=['Player Surname', 'Team', 'Time Played', 'Goals', 'Assists', 'Clean Sheets',
                                             'Saves from Penalty', 'Saves Made', 'Yellow Cards', 'Red Cards',
                                             'Successful Dribbles', 'Shots Off Target inc woodwork',
                                             'Shots On Target inc goals', 'Key Passes', 'Big Chances',
                                             'Successful crosses in the air', 'Total Clearances', 'Blocks',
                                             'Interceptions', 'Recoveries', 'Tackles Won', 'Winning Goal',
                                             'Total Successful Passes All', 'Penalties Conceded',
                                             'Error leading to Goal', 'Error leading to Attempt',
                                             'Tackles Lost', 'Total Fouls Conceded', 'Offsides'])

    league_list = make_collapsible_tree()
    
    with open('static\leaguejson\league.json', 'w') as f:
            json.dump(league_list, f)
    
    player_names = list(premier_league_data.index.values)
    premier_league_data.index.names = ['Player Name']
    premier_league_data.columns.names = ['Attributes']
    del premier_league_data['Team']
    premier_league_data = premier_league_data.set_index(['Player Surname'])
    scaler = MinMaxScaler()
    premier_league_data = pd.DataFrame(scaler.fit_transform(premier_league_data), columns=premier_league_data.columns)

    app.run(host='0.0.0.0', port=8086, debug=True, use_reloader=False)
