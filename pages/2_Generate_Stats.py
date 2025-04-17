import streamlit as st
from streamlit_extras.stylable_container import stylable_container
import pandas as pd
import datetime as dt
from io import BytesIO


#To Do
# Stats Visualisation? 

st.set_page_config(page_title="Generate Player Stats", page_icon="🧐")

st.title("Generate Player Stats! 🧐")
uploaded_file = st.file_uploader("Upload Game Logs Excel", type=["xlsx", "xls"])


if uploaded_file is not None:
    # Load the Excel file
    xls = pd.ExcelFile(uploaded_file)

    # Get sheet names
    sheet_names = xls.sheet_names
    #st.write("Sheets found:", sheet_names)
    expected = ["Logs", "Score Keeper", "Players"]
    if sheet_names == expected: 

        # Read the selected sheet into a dataframe
        logs_df_uploaded = pd.read_excel(xls, sheet_name=sheet_names[0])
        st.session_state.log_df = logs_df_uploaded
        score_df_uploaded = pd.read_excel(xls, sheet_name=sheet_names[1])
        st.session_state.score_time_df = score_df_uploaded
        players_df_uploaded = pd.read_excel(xls, sheet_name=sheet_names[2])
        st.session_state.line_up_df = players_df_uploaded
        st.success("Game Logs successfully uploaded!")
    else: 
        st.error("Incorrect Excel Format")


#Helper Function to update stats 
def update_stats(player, team, action_type):
    """Helper function to update player statistics"""
    # if player not in stats:
    #     stats[player] = {"team": team,  "kill": 0, "catch": 0, "death": 0, "caught_out": 0}

    if action_type == "kill":
        stats[player]["kill"] += 1
        stats[player]["throws"] +=1
    elif action_type == "catch":
        stats[player]["catch"] += 1
        stats[player]["thrown_at"] += 1
    elif action_type == "caught_out":
        stats[player]["caught_out"] += 1
        stats[player]["throws"] += 1
    elif action_type == "death":
        stats[player]["death"] += 1  
    elif action_type == "killed":
        stats[player]["death"] += 1
        stats[player]["thrown_at"] += 1 
    elif action_type == "throw":
        stats[player]["throws"] += 1
    elif action_type == "thrown_at":
        stats[player]["thrown_at"] += 1 
        
      
            
if st.button("Get Player Stats"): 
    stats = {}    
    
    #initialise players
    for _, row in st.session_state.line_up_df.iterrows():
        player = row["player"]
        team = row["team"]
        sets_played = row["sets_played"]
        number_of_sets_played = row["number_of_sets_played"]
        if player not in stats:
            stats[player] = {"team": team, "catch": 0, "kill": 0, "caught_out": 0, "death": 0, "throws":0, "thrown_at": 0, "kill_rate": 0, "sets_played": sets_played, "number_of_sets_played": number_of_sets_played  }
    
    #count stats for each player    
    for _, row in st.session_state.log_df.iterrows():
        set_number = row["set_number"]
        player = row["player"]
        team = row["team"]
        action = row["action"].lower()
        affected_player = row["affected_player"]
        affected_team = row["affected_team"]
        deflection = row["deflection"]
        
        # Update stats based on action
        if action == "kill":
            update_stats(player, team, "kill")
            update_stats(affected_player, affected_team, "killed")
            if deflection == True: 
                stats[player]["throws"] -=1
                stats[affected_player]["thrown_at"] -= 1 
        elif action == "catch":
            update_stats(player, team, "catch")
            update_stats(affected_player, affected_team, "caught_out")
            if deflection == True: 
                stats[affected_player]["throws"] -=1
                stats[player]["thrown_at"] -= 1 
        elif action == "step line": 
            update_stats(player, team, "death")
        elif action == "throw/miss": 
            update_stats(player, team, "throw")
            update_stats(affected_player, affected_team, "thrown_at")
            
        
            

    # Formatting  
    stats_df = pd.DataFrame.from_dict(stats, orient="index").reset_index()
    stats_df.rename(columns={"index": "player"}, inplace=True)
    
    # Add effectiveness column
    stats_df["kill_rate"] = (
        stats_df["kill"]/stats_df["throws"]
    )
    
    stats_df["kill_rate"] = stats_df["kill_rate"].fillna(0)
    
    # Add player_value column
    stats_df["player_value"] = (
        stats_df["kill"] - stats_df["death"] + stats_df["catch"] * 2 - stats_df["caught_out"] * 2
    )

    # Add avg_player_value column (avoid division by zero)
    stats_df["avg_player_value"] = stats_df["player_value"] / stats_df["number_of_sets_played"]
    stats_df["avg_player_value"] = stats_df["avg_player_value"].fillna(0)  # Replace NaN with 0
    
    
    home_team = st.session_state.score_time_df.columns[2]
    away_team = st.session_state.score_time_df.columns[3]
    
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
    home_score = st.session_state.score_time_df.iloc[-1][home_team]
    away_score = st.session_state.score_time_df.iloc[-1][away_team]

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












