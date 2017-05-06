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
    player_id_list = list()         # Stores the ID of each player
    stats_list = list()             # Stores the stats of each player
    teams_dict = dict()             # Maps the player to his particular club
    player_dict = dict()            # Maps the statistics to a player

    for team in premier_league_data.loc[:, "Team"]:
        teams.append(team)
        if team not in club_list:
            club_list.append(team)
            teams_dict[team] = []

    i = 0
    for index, row in premier_league_data.loc[:, ['Player Surname','Time Played', 'Goals', 'Position Id', 'Big Chances', 'Total Fouls Conceded']].iterrows():
        surname = row['Player Surname']
        player_id = int(index)
        position_id = int(row['Position Id'])

        if position_id == 1:
            position = 'Goalkeeper'
        elif position_id == 2:
            position = 'Defender'
        elif position_id == 4:
            position = 'Midfielder'
        elif position_id == 6:
            position = 'Striker'

        player_list.append(surname)
        player_id_list.append(player_id)
        player_dict[player_id] = []
        stats_dict = {"Position": position, "Time Played": row['Time Played'], "Goals": row['Goals']}
        stats_list.append([stats_dict])
        team_logo = 'static/lib/images/logos/' + teams[i] + '.png'
        i += 1
        # player_dict[surname].append({"name": "Position: " + position, "size": "Position: "})
        # player_dict[surname].append({"name": "Time Played: " + str(row['Time Played']), "size": "Time Played: "})
        # player_dict[surname].append({"name": "Goals: " + str(row['Goals']), "size": "Goals: "})
        player_dict[player_id].append(position)
        player_dict[player_id].append(row['Time Played'])
        player_dict[player_id].append(row['Goals'])
        player_dict[player_id].append(team_logo)
        player_dict[player_id].append(row['Big Chances'])
        player_dict[player_id].append(row['Total Fouls Conceded'])
        player_dict[player_id].append(player_baps_dict[index])

    i = 0
    team_list = list()
    for p_id in player_id_list:
        team_jersey = 'static/lib/images/jerseys/' + teams[i] + '.png'
        player_image = 'static/lib/images/players/' + player_mapping_dict[p_id] + '.png'
        teams_dict[teams[i]].append({"name": player_mapping_dict[p_id], "jersey_image": team_jersey, "player_image": player_image,
                                     "position": player_dict[p_id][0], "time_played": player_dict[p_id][1],
                                     "goals": player_dict[p_id][2], "player_logo": player_dict[p_id][3],
                                     "bigchances": player_dict[p_id][4], "totalFouls": player_dict[p_id][5],
                                     "index_values": player_dict[p_id][6]})
        # player_stats_list.append({"name": player, "children": player_dict[player]})
        i += 1

    for team in teams_dict:
        team_logo = 'static/lib/images/logos/' + team + '.png'
        team_list.append({"name":team, "image": team_logo, "children": teams_dict[team]})

    premier_league_logo = 'static/lib/images/logos/Pl_logo.png'
    league_dict = {"name": "English Premier League", "image": premier_league_logo, "children": team_list}
    return league_dict


def get_bps_score(row):
    bps_score = 0
    # BPS for Minutes Played
    if int(row['Time Played']) > 0 and int(row['Time Played']) < 60:
        bps_score += 3
    elif int(row['Time Played']) > 60:
        bps_score += 6

    # BPS for scoring a goal based on position
    if int(row['Position Id']) == 1 and int(row['Goals']) > 0:
        bps_score += 12 * int(row['Goals'])
    elif int(row['Position Id']) == 2 and int(row['Goals']) > 0:
        bps_score += 12 * int(row['Goals'])
    elif int(row['Position Id']) == 4 and int(row['Goals']) > 0:
        bps_score += 18 * int(row['Goals'])
    elif int(row['Position Id']) == 6 and int(row['Goals']) > 0:
        bps_score += 24 * int(row['Goals'])

    # BPS for getting an assist
    if int(row['Assists']) > 0:
        bps_score += 9 * int(row['Assists'])

    # BPS for Goalkeeper and defender keeping a Cleansheet
    if int(row['Position Id']) == 1 and int(row['Clean Sheets']) > 0:
        bps_score += 12
    elif int(row['Position Id']) == 2 and int(row['Clean Sheets']) > 0:
        bps_score += 12

    # BPS for Saving a penalty
    if int(row['Saves from Penalty']) > 0:
        bps_score += 15 * int(row['Saves from Penalty'])

    # BPS for Saves
    if int(row['Saves Made']) > 0:
        bps_score += 2 * int(row['Saves Made'])

    # BPS for successful open play cross
    if int(row['Successful open play crosses']) > 0:
        bps_score += 1 * int(row['Successful open play crosses'])

    # BPS for Big Chance
    if int(row['Big Chances']) > 0:
        bps_score += 3 * int(row['Big Chances'])

    # BPS for clearances, blocks and interceptions
    if int(row['Total Clearances']) > 0 or int(row['Blocks']) > 0 or int(row['Interceptions']) > 0:
        total_val = (int(row['Total Clearances']) + int(row['Blocks']) + int(row['Interceptions'])) / 2
        bps_score += 1 * total_val

    # BPS for recoveries
    if int(row['Recoveries']) > 0:
        bps_score += 1 * (int(row['Recoveries']) / 3)

    # BPS for key passes
    if int(row['Key Passes']) > 0:
        bps_score += 1 * int(row['Key Passes'])

    # BPS for net successful tackles
    if (int(row['Tackles Won']) - int(row['Tackles Lost'])) > 0:
        bps_score += 2 * (int(row['Tackles Won']) - int(row['Tackles Lost']))

    # BPS for successful dribbles
    if int(row['Successful Dribbles']) > 0:
        bps_score += 1 * int(row['Successful Dribbles'])

    # BPS for winning goal
    if int(row['Winning Goal']) > 0:
        bps_score += 3

    # BPS for pass completion rate
    if int(row['Total Successful Passes All']) > 0 or int(row['Total Unsuccessful Passes All']) > 0:
        total_passes = int(row['Total Successful Passes All']) + int(row['Total Unsuccessful Passes All'])
        pass_completion = (int(row['Total Successful Passes All']) * 100) / total_passes
        if total_passes > 30 and (pass_completion > 70 and pass_completion < 79):
            bps_score += 2
        elif total_passes > 30 and (pass_completion > 80 and pass_completion < 89):
            bps_score += 4
        elif total_passes > 30 and (pass_completion > 90):
            bps_score += 6

    # BPS for conceding a penalty
    if int(row['Penalties Conceded']) > 0:
        bps_score -= 3 * int(row['Penalties Conceded'])

    # BPS for missing a penalty
    if int(row['Penalties Not Scored']) > 0:
        bps_score -= 6 * int(row['Penalties Not Scored'])

    # BPS for getting a yellow card
    if int(row['Yellow Cards']) > 0:
        bps_score -= 3

    # BPS for getting a red card
    if int(row['Red Cards']) > 0:
        bps_score -= 9

    # BPS for scoring an own goal
    if int(row['Other Goals']) > 0:
        bps_score -= 6 * int(row['Other Goals'])

    # BPS for making an error leading to goal
    if int(row['Error leading to Goal']) > 0:
        bps_score -= 3 * int(row['Error leading to Goal'])

    # BPS for making an error leading to attempt
    if int(row['Error leading to Attempt']) > 0:
        bps_score -= int(row['Error leading to Attempt'])

    # BPS for total fouls conceded
    if int(row['Total Fouls Conceded']) > 0:
        bps_score -= int(row['Total Fouls Conceded'])

    # BPS for being caught offside
    if int(row['Offsides']) > 0:
        bps_score -= int(row['Offsides'])

    # BPS for being caught offside
    if int(row['Shots Off Target inc woodwork']) > 0:
        bps_score -= int(row['Shots Off Target inc woodwork'])

    return bps_score


def calculate_bps():
    bps_score_dict = dict()
    top_10_baps = [0] * 10
    top_10_players = [''] * 10

    for p_id in player_ids:
        player_baps_dict[p_id] = [0] * 38

    gameweek = 1
    bps_score_dict[str(gameweek)] = []

    for index, row in gameweek_premier_league_data.loc[:,:].iterrows():
        if int(index) > gameweek:
            bps_score_dict[str(gameweek)].append({"top_10_index": top_10_baps})
            bps_score_dict[str(gameweek)].append({"top_10_players": top_10_players})
            gameweek += 1
            bps_score_dict[str(gameweek)] = []
            top_10_baps = [0] * 10
            top_10_players = [''] * 10

        bps_score = get_bps_score(row)

        if bps_score > min(top_10_baps):
            lowest_score_index = top_10_baps.index(min(top_10_baps))
            top_10_baps[lowest_score_index] = bps_score
            top_10_players[lowest_score_index] = row['Player Surname']

        player_baps_dict[int(row['Player ID'])][index-1] = bps_score
        bps_score_dict[str(gameweek)].append({"name" : row['Player Surname'], "index": bps_score})

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
                                      usecols=['Player ID', 'Player Surname', 'Team', 'Time Played', 'Position Id', 'Goals', 'Assists',
                                               'Clean Sheets', 'Saves from Penalty', 'Saves Made', 'Yellow Cards', 'Red Cards',
                                               'Successful Dribbles', 'Shots On Target inc goals', 'Key Passes', 'Big Chances',
                                               'Total Clearances', 'Blocks',
                                               'Interceptions', 'Recoveries', 'Tackles Won', 'Tackles Lost', 'Winning Goal',
                                               'Total Successful Passes All', 'Penalties Conceded',
                                               'Tackles Lost', 'Total Fouls Conceded', 'Offsides'])

    gameweek_premier_league_data = pd.read_csv("Premier League 2011-12 Gameweek.csv", header=0,
                                               usecols=['Player ID', 'Player Surname', 'Team', 'Gameweek', 'Time Played',
                                                        'Position Id', 'Goals', 'Assists', 'Clean Sheets',
                                                        'Saves from Penalty', 'Saves Made', 'Yellow Cards', 'Red Cards',
                                                        'Successful Dribbles', 'Shots Off Target inc woodwork',
                                                        'Shots On Target inc goals', 'Key Passes', 'Big Chances',
                                                        'Successful open play crosses', 'Total Clearances', 'Blocks',
                                                        'Interceptions', 'Recoveries', 'Tackles Won', 'Winning Goal',
                                                        'Total Successful Passes All', 'Total Unsuccessful Passes All',
                                                        'Penalties Conceded', 'Error leading to Goal', 'Other Goals',
                                                        'Error leading to Attempt', 'Penalties Not Scored',
                                                        'Tackles Lost', 'Total Fouls Conceded', 'Offsides',
                                                        'Touches open play final third'])

    player_mapping_dict = dict()
    player_baps_dict = dict()

    for index, row in premier_league_data.loc[:,
                      ['Player Surname', 'Player ID']].iterrows():
        player_mapping_dict[int(row['Player ID'])] = row['Player Surname']

    premier_league_data = premier_league_data.set_index(['Player ID'])
    player_ids = list(premier_league_data.index.values)

    gameweek_premier_league_data = gameweek_premier_league_data.set_index(['Gameweek'])

    bps_score_values = calculate_bps()
    # for gameweek in bps_score_values:
    #     maxIndex = max(bps_score_values[gameweek], key=lambda x: x['index'])
    #     print gameweek, maxIndex

    with open(JSON_DIR +'bps.json', 'w') as f:
        json.dump(bps_score_values, f)

    league_dict = make_collapsible_tree()

    with open(JSON_DIR +'league.json', 'w') as f:
        json.dump(league_dict, f)

    premier_league_data = premier_league_data.reset_index()
    del premier_league_data['Team']
    del premier_league_data['Position Id']
    premier_league_data = premier_league_data.set_index(['Player Surname'])
    player_names = list(premier_league_data.index.values)
    premier_league_data.index.names = ['Player Name']
    premier_league_data.columns.names = ['Attributes']

    gameweek_premier_league_data = gameweek_premier_league_data.reset_index()
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
