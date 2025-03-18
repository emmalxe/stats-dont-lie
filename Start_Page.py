import streamlit as st
from streamlit_extras.stylable_container import stylable_container
import pandas as pd
import datetime as dt
from io import BytesIO
import re

# Page Config
st.set_page_config(page_title="Start Page", page_icon="📊")
st.title("Input Team Information")

# Initialize session state for teams, players, and logs
if "home_team" not in st.session_state:
    st.session_state.home_team = ""
if "away_team" not in st.session_state:
    st.session_state.away_team = ""
if "home_players" not in st.session_state: # all home players 
    st.session_state.home_players = []
if "away_players" not in st.session_state: # all away players 
    st.session_state.away_players = []
if "current_home_line_up" not in st.session_state: 
    st.session_state.current_home_line_up = []
if "current_away_line_up" not in st.session_state:
    st.session_state.current_away_line_up = []
if "set_number" not in st.session_state:
    st.session_state.set_number = 1  # Default set number to 1
if "line_up_dict" not in st.session_state: 
    st.session_state.line_up_dict = {}  
if "line_up_df" not in st.session_state: 
    st.session_state.line_up_df = pd.DataFrame()


# Input Player Names 
col1, col2 = st.columns(2)
with col1:
    st.subheader("Home Team")
    st.session_state.home_team = st.text_input("Home Team Name", value=st.session_state.home_team)

    if st.session_state.home_team == "": 
        st.session_state.home_team = "Home Team"

    # Input field for adding multiple players
    new_home_players = st.text_input("Enter Player Names (comma-separated)", key="home_player_input")

    with stylable_container(
                        "add_home_team",
                        css_styles="""
            button {
                background-color: #AEC6CF;  /* blue for Home Team */
                color: black;
                width: 150px;  /* Set width */
            }""",
                    ):
        if st.button("Add Home Players") and new_home_players:
            player_list = [player.strip() for player in new_home_players.split(",") if player.strip()]
            # Add only new players to the list
            for player in player_list:
                if (player not in st.session_state.home_players):
                    st.session_state.home_players.append(player) #all home players 
                    
        # st.divider()



with col2:
    st.subheader("Away Team")
    st.session_state.away_team = st.text_input("Away Team Name", value=st.session_state.away_team)
    if st.session_state.away_team == "": 
        st.session_state.away_team = "Away Team"

    # Input field for adding multiple players
    new_away_players = st.text_input("Enter Player Names (comma-separated)", key="away_player_input")

    with stylable_container(
            "add_away_team",
            css_styles="""
            button {
                background-color: #FF6961;  /* red for away Team */
                color: black;
                width: 150px;  /* Set width */
            }""",
        ):
        #Add a player to list
        if st.button("Add Away Players") and new_away_players:
            player_list = [player.strip() for player in new_away_players.split(",") if player.strip()]
            # Add only new players to the list
            for player in player_list:
                if (player not in st.session_state.away_players) :
                    st.session_state.away_players.append(player) #all away players
       

selected_set = st.number_input("**Current Set Number**", min_value=1, max_value=20, step=1, value=st.session_state.set_number )
st.session_state.set_number = selected_set

column4, column5 = st.columns(2) 
with column4:
     # Select 6 people line up from all players
    st.write(f"#### Select {st.session_state.home_team} Line-Up for Set {st.session_state.set_number}:")
    home_checkbox_states = {}
    for player in st.session_state.home_players:
        # Check if the player is already in the current lineup
        if player in st.session_state.current_home_line_up:
            is_checked = True
        else:
            is_checked = False

        # Create a checkbox and store its state
        home_checkbox_states[player] = st.checkbox(player, value=is_checked)

    # Update the session state with selected players
    selected_home_players = []
    for player, checked in home_checkbox_states.items():
        if checked:
            selected_home_players.append(player)

    st.session_state.current_home_line_up = selected_home_players
    # Display selected players
    if st.session_state.current_home_line_up:
        st.write("Selected Players: " + ", ".join(st.session_state.current_home_line_up))
    else:
        st.write("No players selected.")

with column5:
    # Select 6 people line up from all players
    st.write(f"#### Select {st.session_state.away_team} Line-Up for Set {st.session_state.set_number}:")
    away_checkbox_states = {}
    for player in st.session_state.away_players:
        # Check if the player is already in the current lineup
        if player in st.session_state.current_away_line_up:
            is_checked = True
        else:
            is_checked = False

        # Create a checkbox and store its state
        away_checkbox_states[player] = st.checkbox(player, value=is_checked)

    # Update the session state with selected players
    selected_away_players = []
    for player, checked in away_checkbox_states.items():
        if checked:
            selected_away_players.append(player)

    st.session_state.current_away_line_up = selected_away_players
    # Display selected players
    if st.session_state.current_away_line_up:
        st.write("Selected Players: " + ", ".join(st.session_state.current_away_line_up))
    else:
        st.write("No players selected.")

if st.button("Save Line-Up"):
    # st.session_state.home_line_up_dict[st.session_state.set_number] = st.session_state.current_home_line_up
    # st.session_state.away_line_up_dict[st.session_state.set_number] = st.session_state.current_away_line_up
    # st.write(st.session_state.home_line_up_dict)
    # st.write(st.session_state.away_line_up_dict)
    # Store line-ups in a single dictionary
    st.session_state.line_up_dict[st.session_state.set_number] = {
        f"{st.session_state.home_team}": st.session_state.current_home_line_up,
        f"{st.session_state.away_team}": st.session_state.current_away_line_up
    }
    # Initialize a dictionary to track player participation
    player_sets = {}
    # Iterate through line_up_dict to populate player_sets
    for set_number, teams in st.session_state.line_up_dict.items():
        for team, players in teams.items():
            for player in players:
                if player not in player_sets:
                    player_sets[player] = {
                        "team": team,
                        "sets_played": [],
                        "number_of_sets_played": 0
                    }
                # Add the set number to the list of sets the player played
                player_sets[player]["sets_played"].append(set_number)
                player_sets[player]["number_of_sets_played"] += 1

    # Convert to DataFrame
    player_data = []
    for player, data in player_sets.items():
        player_data.append([player, data["team"], data["sets_played"], data["number_of_sets_played"]])
    df = pd.DataFrame(player_data, columns=["player", "team","sets_played", "number_of_sets_played"])
    st.session_state.line_up_df = df
    st.dataframe(st.session_state.line_up_df)
    
    



            
        
        
        
        
