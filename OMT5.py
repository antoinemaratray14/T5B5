#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 22 12:24:39 2025

@author: antoinemaratray
"""

import streamlit as st
import requests
from requests.auth import HTTPBasicAuth
import matplotlib.pyplot as plt
import numpy as np

# ============================
# Streamlit App Title & Inputs
# ============================
st.title("Statsbomb Team Metrics Visualisation")

st.write("Enter your Statsbomb credentials and select a league, season, and team to visualise your metrics.")

username = st.text_input("Statsbomb Username", value="")
password = st.text_input("Statsbomb Password", type="password")
league_option = st.selectbox("Select League", options=["English PL", "Ligue 1"])
season_option = st.selectbox("Select Season", options=["2024-25", "2023-24"])

# Mapping for leagues and seasons
league_map = {"English PL": "2", "Ligue 1": "7"}
season_map = {"2024-25": "317", "2023-24": "281"}

# ============================
# Define Functions
# ============================
@st.cache_data(show_spinner=False)
def fetch_team_stats(username, password, league_id, season_id):
    url = f"https://data.statsbomb.com/api/v2/competitions/{league_id}/seasons/{season_id}/team-stats"
    response = requests.get(url, auth=HTTPBasicAuth(username, password))
    if response.status_code != 200:
        return None, response.status_code
    return response.json(), response.status_code

def rank_team_metrics(teams_data, input_team_name, ascending_metrics=None):
    """
    For each numeric metric in the team stats, rank all teams and record
    the ranking (and value) for the input team if it falls in the top 5 or bottom 5.
    """
    if ascending_metrics is None:
        ascending_metrics = []
    
    ranking_results = {}
    sample_team = teams_data[0]
    
    # Identify numeric metrics (keys starting with "team_season_").
    metric_keys = [k for k, v in sample_team.items() if k.startswith('team_season_') and isinstance(v, (int, float))]
    
    total_teams = len(teams_data)
    
    for metric in metric_keys:
        if metric in ascending_metrics:
            sorted_teams = sorted(
                teams_data,
                key=lambda t: t.get(metric) if t.get(metric) is not None else float('inf')
            )
        else:
            sorted_teams = sorted(
                teams_data,
                key=lambda t: t.get(metric) if t.get(metric) is not None else float('-inf'),
                reverse=True
            )
        
        for idx, team in enumerate(sorted_teams):
            if team.get('team_name') == input_team_name:
                rank = idx + 1
                value = team.get(metric)
                break
        else:
            continue
        
        if rank <= 5 or rank > total_teams - 5:
            ranking_results[metric] = {'rank': rank, 'value': value}
    
    return ranking_results

def create_table(ax, data, title, total_teams, is_top5=True):
    """
    Build a table in the given Axes object using loc='upper center'
    so that the title appears above the table.
    """
    # Convert data to strings for display in the table
    table_data = []
    for row in data:
        metric_display, rank_val, val = row
        table_data.append([metric_display, str(rank_val), f"{val:.2f}"])
    
    col_labels = ["Metric", "Rank", "Value"]
    
    ax.set_title(title, color="white", pad=10)
    ax.set_facecolor("#9e9e9e")
    ax.axis('off')
    
    table_obj = ax.table(
        cellText=table_data,
        colLabels=col_labels,
        cellLoc='center',
        loc='upper center'
    )
    
    table_obj.auto_set_font_size(False)
    table_obj.set_fontsize(12)
    table_obj.auto_set_column_width(col=list(range(len(col_labels))))
    table_obj.scale(1, 1.2)
    
    for (r, c), cell in table_obj.get_celld().items():
        cell.set_edgecolor("white")
        cell.set_linewidth(1)
        if r == 0:
            cell.set_facecolor("#9e9e9e")
            cell.get_text().set_color("white")
            continue
        
        cell.set_facecolor("#9e9e9e")
        cell.get_text().set_color("white")
        if c == 1:
            rank_val = int(table_data[r-1][1])
            if is_top5:
                norm_val = 1 - (rank_val - 1)*(1 - 0.3)/4
                bg_color = plt.get_cmap("Greens")(norm_val)
                cell.set_facecolor(bg_color)
            else:
                rank_pos = rank_val - (total_teams - 5)
                norm_val = 0.3 + (rank_pos - 1)*(1 - 0.3)/4
                bg_color = plt.get_cmap("Reds")(norm_val)
                cell.set_facecolor(bg_color)

# ============================
# Main: Fetch Data & Display
# ============================
if username and password:
    league_id = league_map[league_option]
    season_id = season_map[season_option]
    
    with st.spinner("Fetching team stats..."):
        teams_data, status = fetch_team_stats(username, password, league_id, season_id)
    
    if teams_data is None:
        st.error(f"Error fetching data from Statsbomb API: {status}")
    else:
        team_names = [team.get('team_name') for team in teams_data]
        input_team_name = st.selectbox("Select your team", team_names)
        
        if input_team_name:
            # Compute rankings
            ascending_metrics = [
                "team_season_ppda",
                "team_season_completed_dribbles_conceded_pg",
                "team_season_corner_goal_ratio_conceded",
                "team_season_corner_shot_ratio_conceded",
                "team_season_corners_conceded_pg",
                "team_season_counter_attacking_shots_conceded_pg",
                "team_season_deep_completions_conceded_pg",
                "team_season_deep_progressions_conceded_pg",
                "team_season_direct_free_kick_goal_ratio_conceded",
                "team_season_direct_free_kick_goals_conceded_pg",
                "team_season_direct_free_kick_shot_ratio_conceded",
                "team_season_direct_free_kick_xg_conceded_pg",
                "team_season_direct_free_kicks_conceded_pg",
                "team_season_failed_dribbles_conceded_pg",
                "team_season_free_kick_goal_ratio_conceded",
                "team_season_free_kick_shot_ratio_conceded",
                "team_season_free_kick_xg_conceded_pg",
                "team_season_free_kicks_conceded_pg",
                "team_season_goals_conceded_pg",
                "team_season_goals_from_corners_conceded_pg",
                "team_season_goals_from_free_kicks_conceded_pg",
                "team_season_goals_from_throw_ins_conceded_pg",
                "team_season_high_press_shots_conceded_pg",
                "team_season_np_shots_conceded_pg",
                "team_season_np_xg_conceded_pg",
                "team_season_np_xg_per_shot_conceded",
                "team_season_np_shot_distance_conceded",
                "team_season_obv_conceded_pg",
                "team_season_obv_defensive_action_conceded_pg",
                "team_season_obv_dribble_carry_conceded_pg",
                "team_season_obv_gk_conceded_pg",
                "team_season_obv_pass_conceded_pg",
                "team_season_obv_shot_conceded_pg",
                "team_season_op_shots_conceded_outside_box_pg",
                "team_season_op_shots_conceded_pg",
                "team_season_op_xg_conceded_pg",
                "team_season_op_shot_distance_conceded",
                "team_season_op_passes_conceded_pg",
                "team_season_passes_conceded_pg",
                "team_season_penalties_conceded_pg",
                "team_season_penalty_goals_conceded_pg",
                "team_season_shots_from_corners_conceded_pg",
                "team_season_shots_from_direct_free_kicks_conceded_pg",
                "team_season_shots_from_free_kicks_conceded_pg",
                "team_season_shots_from_throw_ins_conceded_pg",
                "team_season_shots_in_clear_conceded_pg",
                "team_season_sp_goals_pg_conceded",
                "team_season_sp_goal_ratio_conceded",
                "team_season_sp_pg_conceded",
                "team_season_sp_shot_ratio_conceded",
                "team_season_xg_per_corner_conceded",
                "team_season_xg_per_direct_free_kick_conceded",
                "team_season_xg_per_free_kick_conceded",
                "team_season_xg_per_sp_conceded",
                "team_season_xg_per_throw_in_conceded",
                "team_season_successful_passes_conceded_pg",
                "team_season_yellow_cards_pg",
                "team_season_red_cards_pg", 
                
            ]
            results = rank_team_metrics(teams_data, input_team_name, ascending_metrics)
            total_teams = len(teams_data)
            
            # Separate into top 5 (strengths) and bottom 5 (weaknesses)
            top5_data = []
            bottom5_data = []
            for metric, info in results.items():
                rank = info['rank']
                value = info['value'] if info['value'] is not None else 0.0
                metric_display = metric.replace("team_season_", "").replace("_", " ")
                if metric_display.endswith(" pg"):
                    metric_display = metric_display[:-3]
                if rank <= 5:
                    top5_data.append([metric_display, rank, value])
                else:
                    bottom5_data.append([metric_display, rank, value])
            
            top5_data.sort(key=lambda x: x[1])
            bottom5_data.sort(key=lambda x: x[1])
            
            # ============================
            # Create Two Subplots (Side by Side)
            # ============================
            fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(14, 8))
            fig.set_facecolor("#9e9e9e")  # Gray background
            
            create_table(ax=ax_left, data=top5_data, title="Strengths - Top 5 metrics", total_teams=total_teams, is_top5=True)
            create_table(ax=ax_right, data=bottom5_data, title="Weaknesses - Bottom 5 metrics", total_teams=total_teams, is_top5=False)
            
            plt.subplots_adjust(wspace=0.3, top=0.88, bottom=0.05, left=0.05, right=0.95)
            st.pyplot(fig)
