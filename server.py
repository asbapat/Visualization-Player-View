from __future__ import division
from flask import Flask
from flask import render_template
from flask import request

import numpy as np
import random
import json
import pandas as pd
import sys
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
    player_id_list = list()         # Stores the ID of each player
    stats_list = list()             # Stores the stats of each player
    teams_dict = dict()             # Maps the player to his particular club
    player_dict = dict()            # Maps the statistics to a player

    color_dict = {"Arsenal": "#FE343B", "Aston Villa": "#FF47A3", "Blackburn Rovers": "#316ED8",
                  "Bolton Wanderers": "#4762C2", "Chelsea": "#045FC8", "Everton": "#416AC8", "Fulham": "#B0ABAD",
                  "Liverpool": "#FF4769", "Manchester City": "#5CBFEB", "Manchester United": "#FD5D65",
                  "Newcastle United": "#B2A9AB", "Norwich City": "#00A150", "Queens Park Rangers": "#5CB3FF",
                  "Stoke City": "#EC8385", "Sunderland": "#F47C88", "Swansea City": "#EBEBEB",
                  "Tottenham Hotspur": "#EBF1FF", "West Bromwich Albion": "#A3AFF5", "Wigan Athletic": "#99CFFF",
                  "Wolverhampton Wanderers": "#E67C2F"}

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
        team_name = teams[i]
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
        player_dict[player_id].append(color_dict[team_name])
        player_dict[player_id].append(player_baps_dict[index])
        player_dict[player_id].append(player_goals_dict[index])
        player_dict[player_id].append(player_assists_dict[index])
        player_dict[player_id].append(player_attempts_dict[index])
        player_dict[player_id].append(player_passes_dict[index])

    i = 0
    team_list = list()
    for p_id in player_id_list:
        team_jersey = 'static/lib/images/jerseys/' + teams[i] + '.png'
        player_image = 'static/lib/images/players/' + player_mapping_dict[p_id] + '.png'
        teams_dict[teams[i]].append({"name": player_mapping_dict[p_id], "jersey_image": team_jersey, "player_image": player_image,
                                     "position": player_dict[p_id][0], "time_played": player_dict[p_id][1],
                                     "goals": player_dict[p_id][2], "player_logo": player_dict[p_id][3],
                                     "bigchances": player_dict[p_id][4], "totalFouls": player_dict[p_id][5],
                                     "team_color": player_dict[p_id][6], "index_values": player_dict[p_id][7],
                                     "goal_values": player_dict[p_id][8], "assist_values": player_dict[p_id][9],
                                     "attempts_values": player_dict[p_id][10], "passes_values": player_dict[p_id][11]})
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
        total_val = math.floor((int(row['Total Clearances']) + int(row['Blocks']) + int(row['Interceptions'])) / 2)
        bps_score += 1 * total_val

    # BPS for recoveries
    if int(row['Recoveries']) > 0:
        bps_score += 1 * math.floor((int(row['Recoveries']) / 3))

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


def calculate_gameweek_details():
    bps_score_dict = dict()
    top_10_baps = [0] * 5
    top_10_players = [''] * 5
    top_10_id = [0] * 5
    home_team = list()
    away_team = list()
    headed = left_foot = right_foot = own_goals = 0
    def_goals = mid_goals = forward_goals = 0
    open_play_attempt = corners_attempt = throws_attempt = free_kick_attempt = set_play_attempt = penalty_attempt = 0
    def_passes = mid_passes = final_passes = 0
    pass_forward = pass_backward = pass_left = pass_right = 0
    saves_inside = saves_outside = saves_penalty = 0
    succ_left_cross = succ_right_cross = unsucc_left_cross = unsucc_right_cross = 0
    headed_clearance = other_clearance = off_line_clearance = 0

    for p_id in player_ids:
        player_baps_dict[p_id] = [0] * 39
        player_goals_dict[p_id] = [0] * 39
        player_assists_dict[p_id] = [0] * 39
        player_attempts_dict[p_id] = [0] * 39
        player_passes_dict[p_id] = [0] * 39

    gameweek = 1
    bps_score_dict[str(gameweek)] = list()

    for index, row in gameweek_premier_league_data.loc[:, :].iterrows():
        if int(index) > gameweek:
            goals_by_type = list()
            attempts = list()
            goals_by_position = list()
            passes = list()
            pass_direction = list()
            saves_made = list()
            crosses = list()
            clearances = list()
            new_radar = list()

            top_10_baps, top_10_players, top_10_id = (list(t) for t in zip(*sorted(zip(top_10_baps, top_10_players, top_10_id), reverse=True)))

            goals_by_type.extend([headed, left_foot, right_foot, own_goals])
            goals_by_position.extend([def_goals, mid_goals, forward_goals])
            attempts.extend([open_play_attempt, corners_attempt, throws_attempt, free_kick_attempt, set_play_attempt, penalty_attempt])
            passes.extend([def_passes, mid_passes, final_passes])
            pass_direction.extend([pass_forward, pass_backward, pass_left, pass_right])
            saves_made.extend([saves_inside, saves_outside, saves_penalty])
            crosses.extend([succ_left_cross, unsucc_left_cross, succ_right_cross, unsucc_right_cross])
            clearances.extend([headed_clearance, other_clearance, off_line_clearance])

            min_goals = min_assists = min_passes = min_attempts = min_baps = sys.maxint
            max_goals = max_assists = max_passes = max_attempts = max_baps = -sys.maxint
            for p_id in top_10_id:
                if player_goals_dict[p_id][gameweek - 1] > max_goals:
                    max_goals = player_goals_dict[p_id][gameweek - 1]
                if player_goals_dict[p_id][gameweek - 1] < min_goals:
                    min_goals = player_goals_dict[p_id][gameweek - 1]

                if player_assists_dict[p_id][gameweek - 1] > max_assists:
                    max_assists = player_assists_dict[p_id][gameweek - 1]
                if player_assists_dict[p_id][gameweek - 1] < min_assists:
                    min_assists = player_assists_dict[p_id][gameweek - 1]

                if player_passes_dict[p_id][gameweek - 1] > max_passes:
                    max_passes = player_passes_dict[p_id][gameweek - 1]
                if player_passes_dict[p_id][gameweek - 1] < min_passes:
                    min_passes = player_passes_dict[p_id][gameweek - 1]

                if player_attempts_dict[p_id][gameweek - 1] > max_attempts:
                    max_attempts = player_attempts_dict[p_id][gameweek - 1]
                if player_attempts_dict[p_id][gameweek - 1] < min_attempts:
                    min_attempts = player_attempts_dict[p_id][gameweek - 1]

                if player_baps_dict[p_id][gameweek - 1] > max_baps:
                    max_baps = player_baps_dict[p_id][gameweek - 1]
                if player_baps_dict[p_id][gameweek - 1] < min_baps:
                    min_baps = player_baps_dict[p_id][gameweek - 1]

            if min_goals == max_goals:
                max_goals = min_goals + 1
                min_goals -= 1
            if min_assists == max_assists:
                max_assists = min_assists + 1
                min_assists -= 1
            if min_passes == max_passes:
                max_passes = min_passes + 1
                min_passes -= 1
            if min_attempts == max_attempts:
                max_attempts = min_attempts + 1
                min_attempts -= 1
            if min_baps == max_baps:
                max_baps = min_baps + 1
                min_baps -= 1

            for p_id in top_10_id:
                radar_data = list()
                radar_data.append({"axis": "Goals", "value": ((player_goals_dict[p_id][gameweek - 1] - min_goals) / (max_goals - min_goals))})
                radar_data.append({"axis": "Assists", "value": ((player_assists_dict[p_id][gameweek - 1] - min_assists) / (max_assists - min_assists))})
                radar_data.append({"axis": "Passes", "value": ((player_passes_dict[p_id][gameweek - 1] - min_passes) / (max_passes - min_passes))})
                radar_data.append({"axis": "Attempts", "value": ((player_attempts_dict[p_id][gameweek - 1] - min_attempts) / (max_attempts - min_attempts))})
                radar_data.append({"axis": "Index", "value": ((player_baps_dict[p_id][gameweek - 1] - min_baps) / (max_baps - min_baps))})
                new_radar.append(radar_data)

            bps_score_dict[str(gameweek)].insert(0, {"top_10_players": top_10_players})
            bps_score_dict[str(gameweek)].insert(1, {"top_10_index": top_10_baps})
            bps_score_dict[str(gameweek)].insert(2, {"values": goals_by_type, "legend": ["Headed", "Left Foot",
                                                        "Right Foot", "Own Goal"]})
            bps_score_dict[str(gameweek)].insert(3, {"values": goals_by_position, "legend": ["Defender Goals",
                                                        "Midfielder Goals", "Striker Goals",]})
            bps_score_dict[str(gameweek)].insert(4, {"values": attempts, "legend": ["Open Play", "Corners", "Throws",
                                                        "Free Kick", "Set Play", "Penalty"]})
            bps_score_dict[str(gameweek)].insert(5, {"values": passes, "legend": ["Defensive Third", "Middle Third",
                                                        "Final Third"]})
            bps_score_dict[str(gameweek)].insert(6, {"values": pass_direction, "legend": ["Forward",
                                                        "Backward", "Left", "Right"]})
            bps_score_dict[str(gameweek)].insert(7, {"values": saves_made, "legend": ["Inside Box", "Outside Box",
                                                        "Penalty"]})
            bps_score_dict[str(gameweek)].insert(8, {"values" : crosses, "legend": ["Successful Left",
                                                        "Unsuccessful Left", "Successful Right",
                                                        "Unsuccessful Right"]})
            bps_score_dict[str(gameweek)].insert(9, {"values": clearances, "legend": ["Headed", "Other",
                                                        "Off the line"]})
            bps_score_dict[str(gameweek)].insert(10, new_radar)
            bps_score_dict[str(gameweek)].insert(11, {"top_10_id": top_10_id})
            gameweek += 1
            bps_score_dict[str(gameweek)] = list()
            top_10_baps = [0] * 5
            top_10_players = [''] * 5
            top_10_id = [0] * 5
            home_team = list()
            away_team = list()
            headed = left_foot = right_foot = own_goals = 0
            def_goals = mid_goals = forward_goals = 0
            open_play_attempt = corners_attempt = throws_attempt = free_kick_attempt = set_play_attempt = penalty_attempt = 0
            def_passes = mid_passes = final_passes = 0
            pass_forward = pass_backward = pass_left = pass_right = 0
            saves_inside = saves_outside = saves_penalty = 0
            succ_left_cross = succ_right_cross = unsucc_left_cross = unsucc_right_cross = 0
            headed_clearance = other_clearance = off_line_clearance = 0

        bps_score = get_bps_score(row)
        total_passes = 0
        total_attempts = 0

        if row['Venue'] == 'Home':
            if row['Team'] not in home_team:
                home_team.append(row['Team'])
                away_team.append(row['Opposition'])
        elif row['Venue'] == 'Away':
            if row['Team'] not in away_team:
                home_team.append(row['Opposition'])
                away_team.append(row['Team'])

        # Calculate Goals by Type
        if int(row['Headed Goals']) > 0:
            headed += int(row['Headed Goals'])
        if int(row['Left Foot Goals']) > 0:
            left_foot += int(row['Left Foot Goals'])
        if int(row['Right Foot Goals']) > 0:
            right_foot += int(row['Right Foot Goals'])
        if int(row['Other Goals']) > 0:
            own_goals += int(row['Other Goals'])

        # Calculate Goals by Position
        if int(row['Position Id']) == 1 and int(row['Goals']) > 0:
            def_goals += int(row['Goals'])
        elif int(row['Position Id']) == 2 and int(row['Goals']) > 0:
            def_goals += int(row['Goals'])
        elif int(row['Position Id']) == 4 and int(row['Goals']) > 0:
            mid_goals += int(row['Goals'])
        elif int(row['Position Id']) == 6 and int(row['Goals']) > 0:
            forward_goals += int(row['Goals'])

        # Calculate Attempts
        if int(row['Attempts Open Play on target']) > 0 or int(row['Attempts Open Play off target']) > 0:
            open_play_attempt += int(row['Attempts Open Play on target']) + int(row['Attempts Open Play off target'])
            total_attempts += int(row['Attempts Open Play on target']) + int(row['Attempts Open Play off target'])
        if int(row['Attempts from Corners on target']) > 0 or int(row['Attempts from Corners off target']) > 0:
            corners_attempt += int(row['Attempts from Corners on target']) + int(row['Attempts from Corners off target'])
            total_attempts += int(row['Attempts from Corners on target']) + int(row['Attempts from Corners off target'])
        if int(row['Attempts from Throws on target']) > 0 or int(row['Attempts from Throws off target']) > 0:
            throws_attempt += int(row['Attempts from Throws on target']) + int(row['Attempts from Throws off target'])
            total_attempts += int(row['Attempts from Throws on target']) + int(row['Attempts from Throws off target'])
        if int(row['Attempts from Direct Free Kick on target']) > 0 or int(row['Attempts from Direct Free Kick off target']) > 0:
            free_kick_attempt += int(row['Attempts from Direct Free Kick on target']) + int(row['Attempts from Direct Free Kick off target'])
            total_attempts += int(row['Attempts from Direct Free Kick on target']) + int(row['Attempts from Direct Free Kick off target'])
        if int(row['Attempts from Set Play on target']) > 0 or int(row['Attempts from Set Play off target']) > 0:
            set_play_attempt += int(row['Attempts from Set Play on target']) + int(row['Attempts from Set Play off target'])
            total_attempts += int(row['Attempts from Set Play on target']) + int(row['Attempts from Set Play off target'])
        if int(row['Attempts from Penalties on target']) > 0 or int(row['Attempts from Penalties off target']) > 0:
            penalty_attempt += int(row['Attempts from Penalties on target']) + int(row['Attempts from Penalties off target'])
            total_attempts += int(row['Attempts from Penalties on target']) + int(row['Attempts from Penalties off target'])

        # Calculate Passes
        if int(row['Successful Passes Defensive third']) > 0 or int(row['Unsuccessful Passes Defensive third']) > 0:
            def_passes += int(row['Successful Passes Defensive third']) + int(row['Unsuccessful Passes Defensive third'])
        if int(row['Successful Passes Middle third']) > 0 or int(row['Unsuccessful Passes Middle third']) > 0:
            mid_passes += int(row['Successful Passes Middle third']) + int(row['Unsuccessful Passes Middle third'])
        if int(row['Successful Passes Final third']) > 0 or int(row['Unsuccessful Passes Final third']) > 0:
            final_passes += int(row['Successful Passes Final third']) + int(row['Unsuccessful Passes Final third'])

        # Calculate Pass Direction
        if int(row['Pass Forward']) > 0:
            pass_forward += int(row['Pass Forward'])
            total_passes += int(row['Pass Forward'])
        if int(row['Pass Backward']) > 0:
            pass_backward += int(row['Pass Backward'])
            total_passes += int(row['Pass Backward'])
        if int(row['Pass Left']) > 0:
            pass_left += int(row['Pass Left'])
            total_passes += int(row['Pass Left'])
        if int(row['Pass Right']) > 0:
            pass_right += int(row['Pass Right'])
            total_passes += int(row['Pass Right'])

        # Calculate saves made
        if int(row['Saves Made from Inside Box']) > 0:
            saves_inside += int(row['Saves Made from Inside Box'])
        if int(row['Saves Made from Outside Box']) > 0:
            saves_outside += int(row['Saves Made from Outside Box'])
        if int(row['Saves from Penalty']) > 0:
            saves_penalty += int(row['Saves from Penalty'])

        # Calculate crosses
        if int(row['Successful Crosses Left']) > 0:
            succ_left_cross += int(row['Successful Crosses Left'])
        if int(row['Unsuccessful Crosses Left']) > 0:
            unsucc_left_cross += int(row['Unsuccessful Crosses Left'])
        if int(row['Successful Crosses Right']) > 0:
            succ_right_cross += int(row['Successful Crosses Right'])
        if int(row['Unsuccessful Crosses Right']) > 0:
            unsucc_right_cross += int(row['Unsuccessful Crosses Right'])

        # Calculate clearances
        if int(row['Headed Clearances']) > 0:
            headed_clearance += int(row['Headed Clearances'])
        if int(row['Other Clearances']) > 0:
            other_clearance += int(row['Other Clearances'])
        if int(row['Clearances Off the Line']) > 0:
            off_line_clearance += int(row['Clearances Off the Line'])

        # Find top 10 players for a gameweek
        if bps_score > min(top_10_baps):
            lowest_score_index = top_10_baps.index(min(top_10_baps))
            top_10_baps[lowest_score_index] = bps_score
            top_10_players[lowest_score_index] = row['Player Surname']
            top_10_id[lowest_score_index] = int(row['Player ID'])

        player_baps_dict[int(row['Player ID'])][index-1] = bps_score
        player_goals_dict[int(row['Player ID'])][index - 1] = int(row['Goals'])
        player_assists_dict[int(row['Player ID'])][index - 1] = int(row['Assists'])
        player_passes_dict[int(row['Player ID'])][index - 1] = total_passes
        player_attempts_dict[int(row['Player ID'])][index - 1] = total_attempts
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


@app.route("/pca", methods=['GET', 'POST'])
def perform_pca():
    global selected
    gameweek = request.args.get('post', 0, type=int)

    # For first page reload
    if gameweek == 0:
        gameweek = 1

    # Perform PCA on the data based on best PCA attributes
    pca = PCA(n_components=3).fit(gameweeks_dataframe[gameweek])

    pca = pca.transform(gameweeks_dataframe[gameweek])

    distance_matrix = metrics.pairwise_distances(pca, metric='euclidean')
    mds = MDS(n_components=2, dissimilarity='precomputed')
    mds = mds.fit_transform(distance_matrix)

    sample_player_names = list()
    for player_id in gameweeks_dataframe[gameweek].index.values:
        sample_player_names.append(player_mapping_dict[player_id])

    se = pd.DataFrame(sample_player_names)
    # pca = np.concatenate((pca, se), axis=1)
    mds = np.concatenate((mds, se), axis=1)

    # pca_values = pd.DataFrame(pca)
    # pca_values.columns = ['PCA1', 'PCA2', 'PCA3', 'PCA4', 'PCA5', 'Name']
    # json_values = pca_values.to_json(orient='records')

    mds_values = pd.DataFrame(mds)
    mds_values.columns = ['MDS1', 'MDS2', 'Name']
    json_values = mds_values.to_json(orient='records')

    with open(JSON_DIR + 'players_pca_json.json', 'w') as f:
        f.write(json_values)

    return json_values


if __name__ == "__main__":
    premier_league_data = pd.read_csv("Premier League 2011-12.csv", header=0,
                                      usecols=['Player ID', 'Player Surname', 'Team', 'Time Played', 'Position Id',
                                               'Goals', 'Assists', 'Clean Sheets', 'Saves from Penalty', 'Saves Made',
                                               'Yellow Cards', 'Red Cards', 'Successful Dribbles',
                                               'Shots On Target inc goals', 'Key Passes', 'Big Chances',
                                               'Total Clearances', 'Blocks', 'Winning Goal',
                                               'Interceptions', 'Recoveries', 'Tackles Won', 'Tackles Lost',
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
                                                        'Touches open play final third', 'Opposition', 'Venue',
                                                        'Headed Goals', 'Left Foot Goals', 'Right Foot Goals',
                                                        'Attempts Open Play on target', 'Attempts from Corners on target',
                                                        'Attempts from Throws on target',
                                                        'Attempts from Direct Free Kick on target',
                                                        'Attempts from Set Play on target', 'Attempts from Penalties on target',
                                                        'Attempts Open Play off target', 'Attempts from Corners off target',
                                                        'Attempts from Throws off target',
                                                        'Attempts from Direct Free Kick off target',
                                                        'Attempts from Set Play off target', 'Attempts from Penalties off target',
                                                        'Successful Passes Defensive third', 'Unsuccessful Passes Defensive third',
                                                        'Successful Passes Middle third', 'Unsuccessful Passes Middle third',
                                                        'Successful Passes Final third', 'Unsuccessful Passes Final third',
                                                        'Pass Forward', 'Pass Backward', 'Pass Left', 'Pass Right',
                                                        'Saves Made from Inside Box', 'Saves Made from Outside Box',
                                                        'Saves from Penalty', 'Successful Crosses Left', 'Unsuccessful Crosses Left',
                                                        'Successful Crosses Right', 'Unsuccessful Crosses Right',
                                                        'Headed Clearances', 'Other Clearances', 'Clearances Off the Line'])

    pca_data_frame = pd.read_csv("Premier League 2011-12 Gameweek.csv", header=0,
                                               usecols=['Player ID', 'Gameweek', 'Time Played',
                                                        'Goals', 'Assists', 'Clean Sheets', 'Red Cards', 'Yellow Cards',
                                                        'Saves from Penalty', 'Big Chances', 'Winning Goal'])

    player_mapping_dict = dict()
    player_baps_dict = dict()
    player_goals_dict = dict()
    player_assists_dict = dict()
    player_attempts_dict = dict()
    player_passes_dict = dict()

    for index, row in premier_league_data.loc[:,
                      ['Player Surname', 'Player ID']].iterrows():
        player_mapping_dict[int(row['Player ID'])] = row['Player Surname']

    premier_league_data = premier_league_data.set_index(['Player ID'])
    player_ids = list(premier_league_data.index.values)

    gameweek_premier_league_data = gameweek_premier_league_data.set_index(['Gameweek'])
    pca_data_frame = pca_data_frame.set_index(['Gameweek'])

    # Create unique list of gameweeks
    gameweeks = [i for i in range(1, 39, 1)]

    # Dataframe directory to store all the gameweek data
    gameweeks_dataframe = {gameweek: pd.DataFrame for gameweek in gameweeks}

    for key in gameweeks_dataframe.keys():
        gameweeks_dataframe[key] = pca_data_frame[:][pca_data_frame.index.values == key]
        gameweeks_dataframe[key] = gameweeks_dataframe[key].reset_index()
        gameweeks_dataframe[key] = gameweeks_dataframe[key].set_index(['Player ID'])
        del gameweeks_dataframe[key]['Gameweek']

        scaler = MinMaxScaler()
        gameweeks_dataframe[key][['Time Played',
                                'Goals', 'Assists', 'Clean Sheets', 'Red Cards', 'Yellow Cards',
                                'Saves from Penalty', 'Big Chances', 'Winning Goal']] = \
                scaler.fit_transform(gameweeks_dataframe[key][['Time Played',
                                                        'Goals', 'Assists', 'Clean Sheets', 'Red Cards', 'Yellow Cards',
                                                        'Saves from Penalty', 'Big Chances', 'Winning Goal']])

    bps_score_values = calculate_gameweek_details()

    with open(JSON_DIR +'bps.json', 'w') as f:
        json.dump(bps_score_values, f)

    league_dict = make_collapsible_tree()

    with open(JSON_DIR +'league.json', 'w') as f:
        json.dump(league_dict, f)

    #premier_league_data = premier_league_data.reset_index()
    del premier_league_data['Team']
    del premier_league_data['Position Id']
    premier_league_data = premier_league_data.set_index(['Player Surname'])
    player_names = list(premier_league_data.index.values)
    premier_league_data.index.names = ['Player Name']
    premier_league_data.columns.names = ['Attributes']

    #gameweek_premier_league_data = gameweek_premier_league_data.reset_index()
    del gameweek_premier_league_data['Team']
    del gameweek_premier_league_data['Opposition']
    del gameweek_premier_league_data['Venue']
    del gameweek_premier_league_data['Player Surname']
    del gameweek_premier_league_data['Position Id']

    gameweek_premier_league_data.index.names = ['Gameweek']
    gameweek_premier_league_data.columns.names = ['Attributes']


    scaler = MinMaxScaler()
    premier_league_data = pd.DataFrame(scaler.fit_transform(premier_league_data), columns=premier_league_data.columns)
    gameweek_premier_league_data = pd.DataFrame(scaler.fit_transform(gameweek_premier_league_data),
                                               columns=gameweek_premier_league_data.columns)

    app.run(host='0.0.0.0', port=8086, debug=True, use_reloader=False)
