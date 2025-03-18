import streamlit as st
from streamlit_extras.stylable_container import stylable_container
import pandas as pd
import datetime as dt
from io import BytesIO
import re

# To Do: 
# can upload your intermediate logs and continue from there? 
# add an undo button --> to undo logs but also undo the button colour changes 
# Edit Instructions


st.set_page_config(page_title="Score Keeper", page_icon="💯")

st.title("Stats Dont Lie!☝🏻")
with st.expander("Instructions"):
    st.write("1. **Enter Team & Player Names** - You can add or remove players at any time without affecting previously saved logs.")
    st.write("2. **Log Set Details** - For each set, record the set number and start time. If you need to update the start time, simply save a new timestamp to override the previous one.")
    st.write("3. **Log Events** - Record key events in each set. To delete a log entry, scroll to the bottom and remove the corresponding row.")
    st.write("4. **Update Scores and Reset Button Colours** - Click the 'Reset' Button to reset the colours of the player buttons. Adjust the cumulative score at the end of each set. If you need to update the score , simply save a new score to override the previous one.")
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


if "logs" not in st.session_state:
    st.session_state.logs = []
if "selected_player" not in st.session_state:
    st.session_state.selected_player = None
if "selected_action" not in st.session_state:
    st.session_state.selected_action = None
if "set_start_times" not in st.session_state:
    st.session_state.set_start_times = {}  
if "set_score" not in st.session_state:
    st.session_state.set_score = {} 
if "log_df" not in st.session_state:
    st.session_state.log_df = pd.DataFrame()
if "score_time_df" not in st.session_state: 
    st.session_state.score_time_df = pd.DataFrame()
if "comments" not in st.session_state:
    st.session_state.comments = ""
if "success_message" not in st.session_state:
    st.session_state.success_message = ""
    
# if "home_left" not in st.session_state:
#     st.session_state.home_left = len(st.session_state.current_home_line_up)
# if "away_left" not in st.session_state:
#     st.session_state.away_left = len(st.session_state.current_away_line_up)

# Time selection
st.subheader("Start Time")
time_input = st.text_input(f"Enter Start time of Set {st.session_state.set_number} (HH:MM:SS)", placeholder="00:00:00")
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
        if time_pattern.match(time_input):
            h, m, s = map(int, time_input.split(":"))
            selected_time = dt.datetime.now().replace(hour=h, minute=m, second=s, microsecond=0)
            st.session_state.set_start_times[st.session_state.set_number] = int(selected_time.timestamp())  # Convert to Unix timestamp
            st.success(f"Saved start time for Set {st.session_state.set_number} at {selected_time.strftime('%H:%M:%S')}")
            
        else: 
            st.error("Invalid time format! Please enter in HH:MM:SS format.")

st.subheader(f"Event Logging for Set {st.session_state.set_number}")

# Event logs buttons
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
            
            for player in st.session_state.current_home_line_up:
                if st.button(player, key=f"home_{player}_alive"):
                    st.session_state.selected_player = player
                
    with col12:
        with stylable_container(
            "away_team",
            css_styles="""
            button {
                background-color: #FF6961;  /* red for away Team */
                color: black;
                width: 100px;
            }""",
        ):
            for player in st.session_state.current_away_line_up:
                if st.button(player, key=f"away_{player}_alive", ):
                    st.session_state.selected_player = player
   
    st.write(f"**Selected Player:** {st.session_state.selected_player}")
    
    

with col2:
    with stylable_container(
            "action_button",
            css_styles="""
            button {
                background-color: #D3D3D3;  /* grey for action buttons */
                color: black;
                width: 120px;
            }""",
        ):
    
        actions = ["Kill", "Catch", "Step Line", "Throw/Miss"]
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
                    width: 100px;
                }""",
            ):
                for player in st.session_state.current_home_line_up:
                    if st.button(player, key=f"opponent_home_{player}_alive"):
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
                for player in st.session_state.current_away_line_up:
                    if st.button(player, key=f"opponent_away_{player}_alive"):
                        st.session_state.affected_player = player
                        
        st.write(f"**Affected Player:** {st.session_state.get('affected_player', 'None')}")
        
# Add comments: 
comments = st.text_area("Enter comments about this event:", value=st.session_state.comments)


column1, column2, column3 = st.columns([1,1,4])
# Log Event
with column1:
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
                    player_team = ""

                # Handle "Step Line" action - leave affected player blank
                affected_player = st.session_state.get("affected_player") if st.session_state.selected_action != "Step Line" else ""

                # Determine team of affected player (if applicable)
                if affected_player in st.session_state.home_players:
                    affected_team = st.session_state.home_team
                elif affected_player in st.session_state.away_players:
                    affected_team = st.session_state.away_team
                else:
                    affected_team = ""


                # Create event dictionary with team information
                event = {
                    "set_number": st.session_state.set_number,
                    "player": st.session_state.selected_player,
                    "team": player_team,  # Track player's team
                    "action": st.session_state.selected_action,
                    "affected_player": affected_player,
                    "affected_team": affected_team,  # Track affected player's team
                    "comment": comments
                }
                
                # Handle errors: 
                if event["team"] == event["affected_team"]: 
                    st.error("You have selected players from the same team! Impossible!")
                
                else:
                    st.session_state.logs.append(event)
                    st.session_state.success_message = f"Logged: {event['player']} ({event['team']}) {event['action'].lower()} {event['affected_player']} ({event['affected_team']})"
                    st.session_state.comments = ""   
                    st.rerun()  
    
# Display success message after rerun
if st.session_state.success_message:
    st.success(st.session_state.success_message)
    st.session_state.success_message = ""  # Clear message after displaying       
            
# Score keeper 
st.subheader(f"Cumulative Score as of Set {st.session_state.set_number}")
cold, cole = st.columns(2)
#selected_set_for_score = col.number_input("As of this set", min_value=1, max_value=20, value=1, step=1, key="selected_set_for_score")
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
        st.session_state.set_score[st.session_state.set_number] = (home_score, away_score)  
        st.success(f"Saved score for Set {st.session_state.set_number}! ")



# Display Logs as Table
st.subheader("Game Events")

# Convert logs to a DataFrame
if st.session_state.logs !=[]:
    log_df = pd.DataFrame(st.session_state.logs)
    st.session_state.log_df = log_df
    
    if not log_df.empty:
        for index, row in log_df.tail(5).iterrows():
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
if st.session_state.set_start_times:
    start_time_stamp_df = pd.DataFrame({
        "set_number": st.session_state.set_start_times.keys(),
        "start_time": [dt.datetime.fromtimestamp(timestamp).strftime("%H:%M:%S") for timestamp in st.session_state.set_start_times.values()]
    })
    #st.dataframe(start_time_stamp_df, hide_index = True)

if st.session_state.set_score: 
    cscore_df = pd.DataFrame({
        "set_number": st.session_state.set_score.keys(),
        f"{st.session_state.home_team}": [st.session_state.set_score[set_number][0] for set_number in st.session_state.set_score.keys()],
        f"{st.session_state.away_team}": [st.session_state.set_score[set_number][1] for set_number in st.session_state.set_score.keys()]
    })
    #st.dataframe(cscore_df, hide_index = True)

if st.session_state.set_start_times and st.session_state.set_score : 
    score_time_df = (
    start_time_stamp_df
    .merge(cscore_df, on="set_number", how="outer")
    )
    st.dataframe(score_time_df, hide_index = True)
    st.session_state.score_time_df = score_time_df

player_df = st.session_state.line_up_df
#Save Score and timestamp in csv format 
if st.session_state.log_df is not None and st.session_state.score_time_df is not None:
    log_df = st.session_state.log_df 
    score_time_df = st.session_state.score_time_df
    # create Excel file in-memory 
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        log_df.to_excel(writer, sheet_name="Logs", index=False)
        score_time_df.to_excel(writer, sheet_name="Score Keeper", index=False)
        player_df.to_excel(writer, sheet_name="Players", index=False)
    output.seek(0) 
    
    st.download_button(
        label="Download Excel File",
        data=output,
        file_name= f"{st.session_state.home_team}vs{st.session_state.away_team}_stats.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    


