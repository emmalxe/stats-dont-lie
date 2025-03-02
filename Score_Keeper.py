import streamlit as st
from streamlit_extras.stylable_container import stylable_container
import pandas as pd
import datetime as dt
from io import BytesIO
import re

# To Do: 
# try to make it so that if the person is dead, the button becomes grey, if get caught back then restated. 
# can upload your intermediate logs and continue from there? 
# add remarks button for certain timestamps. 

st.title("Stats Dont Lie!☝🏻")
with st.expander("Instructions"):
    st.write("1. **Enter Team & Player Names** - You can add or remove players at any time without affecting previously saved logs.")
    st.write("2. **Log Set Details** - For each set, record the set number and start time. If you need to update the start time, simply save a new timestamp to override the previous one.")
    st.write("3. **Log Events** - Record key events in each set. To delete a log entry, scroll to the bottom and remove the corresponding row.")
    st.write("4. **Update Scores** - Adjust the cumulative score at the end of each set. If you need to update the score , simply save a new score to override the previous one.")
    st.write("5. **Export & Finalize** - Download your logs as an Excel file, make manual edits if needed, and upload the finalized file on the 'Generate Stats' page to generate player statistics.")
    st.warning("⚠️ Important: If you rerun the page, unsaved data will be lost! Be sure to download your logs! ")
    
st.markdown("""
    <style>
        .stButton > button {
            width: 100px;  /* Set width */
            height: 20px;  /* Set height */
            font-size: 8px;  /* Set font size */
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for teams, players, and logs
if "home_team" not in st.session_state:
    st.session_state.home_team = ""
if "away_team" not in st.session_state:
    st.session_state.away_team = ""
if "home_players" not in st.session_state:
    st.session_state.home_players = []
if "away_players" not in st.session_state:
    st.session_state.away_players = []
if "logs" not in st.session_state:
    st.session_state.logs = []
if "selected_player" not in st.session_state:
    st.session_state.selected_player = None
if "selected_action" not in st.session_state:
    st.session_state.selected_action = None
if "set_number" not in st.session_state:
    st.session_state.set_number = 1  # Default set number to 1
if "set_start_times" not in st.session_state:
    st.session_state.set_start_times = {}  
if "set_score" not in st.session_state:
    st.session_state.set_score = {} 
if "log_df" not in st.session_state:
    st.session_state.log_df = pd.DataFrame()
if "score_time_df" not in st.session_state: 
    st.session_state.score_time_df = pd.DataFrame()

# Input Player Names 
col1, col2 = st.columns(2)
with col1:
    st.subheader("Home Team")
    st.session_state.home_team = st.text_input("Home Team Name", value=st.session_state.home_team)
    
    # Input field for adding multiple players
    #new_home_players = st.text_input("Enter Player Name", key="home_player_input")
    new_home_players = st.text_input("Enter Player Names (comma-separated)", key="home_player_input")
    
    with stylable_container(
            "home_team",
            css_styles="""
            button {
                background-color: #AEC6CF;  /* blue for Home Team */
                color: black;
            }""",
        ):
        if st.button("Add Home"):
            if new_home_players:
                player_list = [player.strip() for player in new_home_players.split(",") if player.strip()]
                # Add only new players to the list
                for player in player_list:
                    if player not in st.session_state.home_players:
                        st.session_state.home_players.append(player)
                
                
with col2:
    st.subheader("Away Team")
    st.session_state.away_team = st.text_input("Away Team Name", value=st.session_state.away_team)
    
    # Input field for adding multiple players
    new_away_players = st.text_input("Enter Player Names (comma-separated)", key="away_player_input")
    
    with stylable_container(
            "away_team",
            css_styles="""
            button {
                background-color: #FF6961;  /* red for away Team */
                color: black;
            }""",
        ):
        #Add a player to list
        if st.button("Add Away"):
            if new_away_players: 
                player_list = [player.strip() for player in new_away_players.split(",") if player.strip()]
                # Add only new players to the list
                for player in player_list:
                    if player not in st.session_state.away_players:
                        st.session_state.away_players.append(player)
             
                        
all_players = st.session_state.home_players + st.session_state.away_players

if (st.session_state.home_players != []) or (st.session_state.away_players != []): 
    col1, col2 = st.columns([1,2])
    with col1: 
        player_to_remove = st.selectbox("Select Player to Remove (if needed)", options=all_players)

    col1, col2 = st.columns([1,3])
    with col1: 
        # Button to remove selected player
        with stylable_container(
                    "remove_player",
                    css_styles="""
                    button {
                        width: 130px;  
                        height: 20px;  
                    }""",
                ):
                if st.button("Remove Player"):
                    if player_to_remove in st.session_state.home_players:
                        st.session_state.home_players.remove(player_to_remove)
                    elif player_to_remove in st.session_state.away_players:
                        st.session_state.away_players.remove(player_to_remove)

                  
                  
st.divider()


# Event Logging

st.subheader("Set number and Start Time")

col1, col2 = st.columns([1,3])
with col1: 
    # Set Number selection 
    selected_set = st.number_input("Set Number", min_value=1, max_value=20, value=st.session_state.set_number, step=1)
    st.session_state.set_number = selected_set
with col2: 
    # Time selection
    # cola,colb,colc = st.columns(3) 
    # hour = cola.number_input("Hour", min_value=0, max_value=23, value=0, step=1)
    # minute = colb.number_input("Minute", min_value=0, max_value=59, value=0, step=1)
    # second = colc.number_input("Second", min_value=0, max_value=59, value=0, step=1)
    time_input = st.text_input("Enter Time (HH:MM:SS)", placeholder="00:00:00")
    time_pattern = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d$")

# Save timestamp when button is clicked
with stylable_container(
    "log_event",
    css_styles="""
    button {
        background-color: #000000;  
        color: white;
    }""",
    ):
    if st.button("Save"):
        # Convert selected time to a timestamp
        # selected_time = dt.datetime.now().replace(hour=hour, minute=minute, second=second, microsecond=0)
        # st.session_state.set_start_times[selected_set] = int(selected_time.timestamp())  # Convert to Unix timestamp
        # st.success(f"Saved start time for Set {selected_set} at {selected_time.strftime('%H:%M:%S')}")
        if time_pattern.match(time_input):
            h, m, s = map(int, time_input.split(":"))
            selected_time = dt.datetime.now().replace(hour=h, minute=m, second=s, microsecond=0)
            st.session_state.set_start_times[selected_set] = int(selected_time.timestamp())  # Convert to Unix timestamp
            st.success(f"Saved start time for Set {selected_set} at {selected_time.strftime('%H:%M:%S')}")
            
        else: 
            st.error("Invalid time format! Please enter in HH:MM:SS format.")
            
            
            


st.subheader(f"Event Logging for Set {st.session_state.set_number}")

# event logs buttons
col1, col2, col3 = st.columns(3)

with col1:
    st.write("Select Player")
    col11, col12 = st.columns(2)
    with col11: 
        
        with stylable_container(
            "home_team",
            css_styles="""
            button {
                background-color: #AEC6CF;  /* blue for Home Team */
                color: black;
            }""",
        ):
            for player in st.session_state.home_players:
                if st.button(player, key=f"home_{player}"):
                    st.session_state.selected_player = player
                
    with col12:
        with stylable_container(
            "away_team",
            css_styles="""
            button {
                background-color: #FF6961;  /* red for away Team */
                color: black;
            }""",
        ):
            for player in st.session_state.away_players:
                if st.button(player, key=f"away_{player}", ):
                    st.session_state.selected_player = player
    st.write(f" **Selected Player:** {st.session_state.selected_player}")

with col2:
    with stylable_container(
            "action_button",
            css_styles="""
            button {
                background-color: #D3D3D3;  /* grey for action buttons */
                color: black;
            }""",
        ):
    
        actions = ["Kill", "Catch", "Step Line"]
        cola, colb, colc = st.columns([1,3,1])
        
        with colb: 
            st.write("Select Action")
            for action in actions:
                if st.button(action, key=f"action_{action}"):
                    st.session_state.selected_action = action

            st.write(f" **Selected Action:** {st.session_state.selected_action}")


with col3: 
        st.write("Select Affected Player")
        col21, col22 = st.columns(2)
        with col21: 
            with stylable_container(
                "home_team",
                css_styles="""
                button {
                    background-color: #AEC6CF;  /* blue for Home Team */
                    color: black;
                }""",
            ):
                for player in st.session_state.home_players:
                    if st.button(player, key=f"opponent_{player}"):
                        st.session_state.affected_player = player
        with col22:                
            with stylable_container(
                "away_team",
                css_styles="""
                button {
                    background-color: #FF6961;  /* red for away Team */
                    color: black;
                }""",
            ):
                for player in st.session_state.away_players:
                    if st.button(player, key=f"opponent_{player}"):
                        st.session_state.affected_player = player
                        
        st.write(f"**Affected Player:** {st.session_state.get('affected_player', 'None')}")

# Log Event
with stylable_container(
    "log_event",
    css_styles="""
    button {
        background-color: #000000;  
        color: white;
    }""",
    ):
    if st.button("Log Event"):
        if (
            st.session_state.selected_player
            and st.session_state.selected_action
        ):
            # Determine team of selected player
            if st.session_state.selected_player in st.session_state.home_players:
                player_team = st.session_state.home_team
            elif st.session_state.selected_player in st.session_state.away_players:
                player_team = st.session_state.away_team
            else:
                player_team = "Unknown"

            # Handle "Step Line" action - leave affected player blank
            affected_player = st.session_state.get("affected_player") if st.session_state.selected_action != "Step Line" else ""

            # Determine team of affected player (if applicable)
            if affected_player in st.session_state.home_players:
                affected_team = st.session_state.home_team
            elif affected_player in st.session_state.away_players:
                affected_team = st.session_state.away_team
            else:
                affected_team = "Unknown"

            # Create event dictionary with team information
            event = {
                "set_number": st.session_state.set_number,
                "player": st.session_state.selected_player,
                "team": player_team,  # Track player's team
                "action": st.session_state.selected_action,
                "affected_player": affected_player,
                "affected_team": affected_team  # Track affected player's team
            }

            # Append the event to the logs
            st.session_state.logs.append(event)
            st.success(f"Logged: {event['player']} ({event['team']}) {event['action'].lower()} {event['affected_player']} ({event['affected_team']})")


# Score keeper 
st.subheader("Cumulative Score")
col, cold, cole = st.columns(3)
selected_set_for_score = col.number_input("As of this set", min_value=1, max_value=20, value=1, step=1, key="selected_set_for_score")
home_score = cold.number_input(f"{st.session_state.home_team}", min_value=0, max_value=20, value=0, step=1, key="home_score")
away_score = cole.number_input(f"{st.session_state.away_team}", min_value=0, max_value=20, value=0, step=1, key="away_score")

with stylable_container(
    "log_event",
    css_styles="""
    button {
        background-color: #000000;  
        color: white;
    }""",
    ):
    if st.button("Save Score"):
        st.session_state.set_score[selected_set_for_score] = (home_score, away_score)  
        st.success(f"Saved score for Set {selected_set_for_score}! ")



# Display Logs as Table
st.subheader("Game Events")

# Convert logs to a DataFrame and display
if st.session_state.logs:
    log_df = pd.DataFrame(st.session_state.logs)
    st.session_state.log_df = log_df
    
    if not log_df.empty:
        for index, row in log_df.iterrows():
            col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 2, 1])
            with col1:
                st.write(row["set_number"])
            with col2:
                st.write(row["player"])
            with col3:
                st.write(row["action"])
            with col4:
                st.write(row["affected_player"])
            with col5:
                if st.button(f"Delete {index}", key=f"delete_{index}"):
                    # Delete the row from the logs
                    st.session_state.logs.pop(index)

# Display stored timestamps
if len(st.session_state.set_start_times) == len(st.session_state.set_score) and len(st.session_state.set_start_times) !=0 : 
    # Convert score and time to df 
    score_time_df = pd.DataFrame({
        "set_number": st.session_state.set_start_times.keys(),
        "start_time": [dt.datetime.fromtimestamp(timestamp).strftime("%H:%M:%S") for timestamp in st.session_state.set_start_times.values()],
        f"{st.session_state.home_team}": [st.session_state.set_score[set_number][0] for set_number in st.session_state.set_start_times.keys()],
        f"{st.session_state.away_team}": [st.session_state.set_score[set_number][1] for set_number in st.session_state.set_start_times.keys()]
    })
    
    st.dataframe(score_time_df, hide_index = True)
    st.session_state.score_time_df = score_time_df


#Save Score and timestamp in csv format 
if len(st.session_state.set_start_times) == len(st.session_state.set_score) and len(st.session_state.set_start_times) !=0 and st.session_state.logs:
    
    # create Excel file in-memory 
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        log_df.to_excel(writer, sheet_name="Logs", index=False)
        score_time_df.to_excel(writer, sheet_name="Score Keeper", index=False)
    output.seek(0) 
    
    st.download_button(
        label="Download Excel File",
        data=output,
        file_name= f"{st.session_state.home_team}vs{st.session_state.away_team}_stats.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    


