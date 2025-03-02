import streamlit as st
from streamlit_extras.stylable_container import stylable_container
import pandas as pd
import datetime as dt
from io import BytesIO


#To Do
# Stats Visualisation

st.title("Generate Player Stats! 🧐")

# # File uploader allows only Excel files
if not st.session_state.log_df.empty and not st.session_state.score_time_df.empty:
    logs_df = st.session_state.log_df
    score_df = st.session_state.score_time_df

uploaded_file = st.file_uploader("Upload Game Logs Excel", type=["xlsx", "xls"])

if uploaded_file is not None:
    # Load the Excel file
    xls = pd.ExcelFile(uploaded_file)
    
    # Get sheet names
    sheet_names = xls.sheet_names
    #st.write("Sheets found:", sheet_names)
    expected = ["Logs", "Score Keeper"]
    if sheet_names == expected: 
        
        # Read the selected sheet into a dataframe
        logs_df = pd.read_excel(xls, sheet_name=sheet_names[0])
        st.session_state.log_df = logs_df
        score_df = pd.read_excel(xls, sheet_name=sheet_names[1])
        st.session_state.score_time_df = score_df
        st.success("Game Logs successfully uploaded!")
    else: 
        st.error("Incorrect Excel Format")
    
    
    
if not st.session_state.log_df.empty: 
    stats = {}   
    # first_team = logs_df.iloc[0]["team"]
    # second_team = logs_df.iloc[0]["affected_team"]
    
    #Helper Function to update stats 
    def update_stats(player, team, action_type):
        """Helper function to update player statistics"""
        if player not in stats:
            stats[player] = {"team": team,  "kill": 0, "catch": 0, "death": 0, "caught_out": 0, "sets_played": set(), "player_value": 0, "avg_player_value": 0}

        if action_type == "kill":
            stats[player]["kill"] += 1
        elif action_type == "catch":
            stats[player]["catch"] += 1
        elif action_type == "caught_out":
            stats[player]["caught_out"] += 1
        elif action_type == "death":
            stats[player]["death"] += 1
            
            
    
    for _, row in logs_df.iterrows():
        set_number = row["set_number"]
        player = row["player"]
        team = row["team"]
        action = row["action"].lower()
        affected_player = row["affected_player"]
        affected_team = row["affected_team"]
        
        # Ensure players are initialized in stats
        if player not in stats:
            stats[player] = {"team": team, "catch": 0, "kill": 0, "caught_out": 0, "death": 0, "sets_played": set(), "player_value": 0, "avg_player_value": 0}
        if affected_player not in stats:
            stats[affected_player] = {"team": affected_team, "catch": 0, "kill": 0, "caught_out": 0, "death": 0, "sets_played": set(), "player_value": 0, "avg_player_value": 0}


        # Track sets played
        stats[player]["sets_played"].add(set_number)
        stats[affected_player]["sets_played"].add(set_number)
        
        # Update stats based on action
        if action == "kill":
            update_stats(player, team, "kill")
            update_stats(affected_player, affected_team, "death")
        elif action == "catch":
            update_stats(player, team, "catch")
            update_stats(affected_player, affected_team, "caught_out")
        elif action == "step line": 
            update_stats(player, team, "death")
            
        
    # Convert sets played to count
    for player in stats:
        stats[player]["sets_played"] = len(stats[player]["sets_played"])
    
    # Formatting  
    stats_df = pd.DataFrame.from_dict(stats, orient="index").reset_index()
    stats_df.rename(columns={"index": "player"}, inplace=True)
    
    # Add player_value column
    stats_df["player_value"] = (
        stats_df["kill"] - stats_df["death"] + stats_df["catch"] * 2 - stats_df["caught_out"] * 2
    )

    # Add avg_player_value column (avoid division by zero)
    stats_df["avg_player_value"] = stats_df["player_value"] / stats_df["sets_played"]
    stats_df["avg_player_value"] = stats_df["avg_player_value"].fillna(0)  # Replace NaN with 0

    home_team = score_df.columns[2]
    away_team = score_df.columns[3]
    # Separate DataFrames for each team
    team_1_df = stats_df[stats_df["team"] == home_team]
    team_2_df = stats_df[stats_df["team"] == away_team]
    
    # Drop the 'team' column from each team's DataFrame
    team_1_df = team_1_df.drop(columns=["team"]).reset_index(drop=True)
    team_2_df = team_2_df.drop(columns=["team"]).reset_index(drop=True)

    # Display statistics for each team separately
    st.write(f"#### **{home_team} player stats**")
    st.dataframe(team_1_df, hide_index = True)

    st.write(f"#### **{away_team} player stats**")
    st.dataframe(team_2_df, hide_index = True)
    
    # Extract the home and away score from the last row
    home_score = score_df.iloc[-1][home_team]
    away_score = score_df.iloc[-1][away_team]

    # Print the final score
    final_score = f"Final Score : {home_score}:{away_score}"
    st.write(final_score)
    
    if home_score == away_score: 
        st.success("It's a Draw!")
    else: 
        if home_score > away_score: 
            winner = home_team
        else:
            winner = away_team
        st.success(f"The winner is....{winner}! 😁")
    
    # Download Stats 
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        team_1_df.to_excel(writer, sheet_name=home_team, index=False)
        team_2_df.to_excel(writer, sheet_name=away_team, index=False)
    output.seek(0)   
    st.download_button(
        label="Download",
        data=output,
        file_name=f"{home_team}vs{away_team}_player_stats.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )












