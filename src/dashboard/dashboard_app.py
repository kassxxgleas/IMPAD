"""
Simple Streamlit dashboard for visualizing a single candidate session log.

Expected input file:
- data/session_log.json

The app shows:
- Summary: key scores and time spent in each state
- Timeline: state changes over time
- Clarity: clarity-related metrics if CLARITY events are present
"""

import json
import os
from typing import List, Dict, Any

import pandas as pd
import altair as alt
import streamlit as st
import sys

# Ensure src modules can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from src.core.leaderboard import Leaderboard


# =========================
# Constants & basic config
# =========================

# Mapping of STATE values to numeric codes for plotting
STATE_TO_CODE: Dict[str, int] = {
    "IDLE": 0,
    "CODING": 1,
    "RESEARCHING": 2,
}

# Page configuration – UI only
st.set_page_config(
    page_title="GlassBox – Process Audit",
    page_icon="📊",
    layout="wide",
)


# =========================
# Data loading & transform
# =========================

def load_session_log(path: str) -> dict:
    """
    Load session log JSON file from the given path and return it as a Python dict.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def events_to_df(events: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Convert a list of event dicts into a pandas DataFrame.

    Adapted to the expected JSON format, for example:

    {
        "ts": 8.01,
        "type": "STATE",
        "payload": {
            "state": "RESEARCHING"
        }
    }

    Output columns:
    - ts: event time in seconds from session start (float)
    - type: event type, e.g. "STATE" or "CLARITY"
    - state: "CODING", "RESEARCHING", "IDLE" or None
    - coherence, terminology, completeness, comment:
      optional clarity-related fields (None/NaN where not present).
    """
    rows: List[Dict[str, Any]] = []

    for ev in events:
        payload = ev.get("payload", {}) or {}

        row: Dict[str, Any] = {
            "ts": ev.get("ts"),
            "type": ev.get("type"),
            "state": payload.get("state"),
            "coherence": payload.get("coherence"),
            "terminology": payload.get("terminology"),
            "completeness": payload.get("completeness"),
            "comment": payload.get("comment"),
        }
        rows.append(row)

    if not rows:
        return pd.DataFrame(
            columns=[
                "ts",
                "type",
                "state",
                "coherence",
                "terminology",
                "completeness",
                "comment",
            ]
        )

    df = pd.DataFrame(rows)

    # Sort by time if possible
    if "ts" in df.columns:
        try:
            df = df.sort_values("ts")
        except Exception:
            # If sorting fails for any reason, keep original order
            pass

    df = df.reset_index(drop=True)
    return df


# =========================
# Metrics computation
# =========================

def compute_basic_metrics(session_data: dict, df_events: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute basic metrics from session summary and STATE events.

    Metrics:
    - hard_score, soft_score, verdict (from session_data["summary"])
    - session_duration_sec (from started_at / ended_at if available, otherwise ts range)
    - coding_time_sec, researching_time_sec, idle_time_sec (from STATE events)
    """
    summary = session_data.get("summary", {}) or {}
    hard_score = summary.get("hard_score")
    soft_score = summary.get("soft_score")
    verdict = summary.get("verdict")

    started_at = session_data.get("started_at")
    ended_at = session_data.get("ended_at")

    # Initialize durations for each known state
    durations: Dict[str, float] = {
        "CODING": 0.0,
        "RESEARCHING": 0.0,
        "IDLE": 0.0,
    }

    if df_events.empty:
        # No events, nothing to compute
        return {
            "hard_score": hard_score,
            "soft_score": soft_score,
            "verdict": verdict,
            "session_duration_sec": 0.0,
            "coding_time_sec": 0.0,
            "researching_time_sec": 0.0,
            "idle_time_sec": 0.0,
        }

    df = df_events.sort_values("ts").reset_index(drop=True)

    # Session duration:
    # - prefer started_at/ended_at if they are numeric (e.g. UNIX timestamps)
    # - otherwise use min/max ts from events
    if isinstance(started_at, (int, float)) and isinstance(ended_at, (int, float)):
        session_total = float(ended_at - started_at)
    else:
        session_total = float(df["ts"].max() - df["ts"].min())

    # Aggregate durations per state using consecutive events
    for i in range(len(df)):
        state = df.loc[i, "state"]
        current_ts = df.loc[i, "ts"]

        if i < len(df) - 1:
            next_ts = df.loc[i + 1, "ts"]
            duration = float(next_ts - current_ts)
        else:
            # Last event: extend until session end if we know it
            if isinstance(started_at, (int, float)) and isinstance(ended_at, (int, float)):
                duration = float(session_total - current_ts)
            else:
                duration = 0.0

        if isinstance(state, str) and state in durations:
            durations[state] += max(duration, 0.0)

    result: Dict[str, Any] = {
        "hard_score": hard_score,
        "soft_score": soft_score,
        "verdict": verdict,
        "session_duration_sec": round(session_total, 2),
        "coding_time_sec": round(durations["CODING"], 2),
        "researching_time_sec": round(durations["RESEARCHING"], 2),
        "idle_time_sec": round(durations["IDLE"], 2),
    }

    return result


# =========================
# UI rendering functions
# =========================

def _format_score(value: Any) -> str:
    """
    Format score to a short string if numeric, otherwise return as-is or N/A.
    """
    if isinstance(value, (int, float)):
        return f"{float(value):.1f}"
    return str(value) if value is not None else "N/A"


def _to_minutes(value: Any) -> float:
    """
    Convert seconds to minutes for display. Non-numeric -> 0.0
    """
    try:
        return float(value) / 60.0
    except (TypeError, ValueError):
        return 0.0


def render_summary_section(metrics: Dict[str, Any]) -> None:
    """
    Render the Summary section with scores and time-based metrics.
    """
    st.divider()
    st.header("Session Summary")
    st.caption(
        "This section gives a quick overview of the candidate’s performance in this session. "
        "Check the Hard and Soft Scores, the final verdict, and how their time was split "
        "between coding, researching, and idle time."
    )

    hard_score = metrics.get("hard_score")
    soft_score = metrics.get("soft_score")
    verdict = metrics.get("verdict")

    session_duration_sec = metrics.get("session_duration_sec")
    coding_time_sec = metrics.get("coding_time_sec")
    researching_time_sec = metrics.get("researching_time_sec")
    idle_time_sec = metrics.get("idle_time_sec")

    session_duration_min = _to_minutes(session_duration_sec)
    coding_time_min = _to_minutes(coding_time_sec)
    researching_time_min = _to_minutes(researching_time_sec)
    idle_time_min = _to_minutes(idle_time_sec)

    # Top row: key scores
    top1, top2, top3 = st.columns(3)
    top1.metric("Hard Score", _format_score(hard_score))
    top2.metric("Soft Score", _format_score(soft_score))

    verdict_value = verdict if verdict is not None else "N/A"
    if isinstance(verdict_value, str):
        verdict_value = verdict_value.upper()

    verdict_display = verdict_value
    if verdict_value == "PASS":
        verdict_display = "✅ PASS"
    elif verdict_value == "FAIL":
        verdict_display = "❌ FAIL"

    top3.metric("Verdict", verdict_display)

    st.markdown("#### Time distribution")

    # Second row: time-related metrics (in minutes)
    t1, t2, t3, t4 = st.columns(4)
    t1.metric("Session duration", f"{session_duration_min:.1f} min")
    t2.metric("Coding time", f"{coding_time_min:.1f} min")
    t3.metric("Researching time", f"{researching_time_min:.1f} min")
    t4.metric("Idle time", f"{idle_time_min:.1f} min")

    st.caption("Time values are shown in minutes, derived from the raw session log.")


def render_timeline_section(df_events: pd.DataFrame) -> None:
    """
    Render the Timeline section with state over time chart using Altair (Gantt style).
    """
    st.divider()
    st.header("Activity Timeline")
    st.caption(
        "This timeline shows how the candidate spent their time during the session: "
        "coding, researching, or idle. Colored bars indicate the duration of each activity."
    )

    if df_events.empty:
        st.warning("No events found in this session.")
        return

    # Use only STATE events for the timeline
    df_timeline = df_events[df_events["type"] == "STATE"].copy()
    if df_timeline.empty:
        st.info("No STATE events to show in the timeline.")
        return

    # 1. Transform events to intervals
    # Sort by time
    df_timeline = df_timeline.sort_values("ts").reset_index(drop=True)
    
    intervals = []
    
    # We need the session end time to close the last interval
    # Try to find it in the original df_events or estimate it
    max_ts = df_events["ts"].max()
    
    for i in range(len(df_timeline)):
        current_state = df_timeline.loc[i, "state"]
        start_time = df_timeline.loc[i, "ts"]
        
        # Determine end time
        if i < len(df_timeline) - 1:
            end_time = df_timeline.loc[i+1, "ts"]
        else:
            # Last event goes until max_ts (or +1s if same)
            end_time = max(max_ts, start_time + 1.0)
            
        duration = end_time - start_time
        
        if duration > 0:
            intervals.append({
                "Activity": current_state,
                "Start": start_time,
                "End": end_time,
                "Duration (s)": round(duration, 1)
            })
            
    if not intervals:
        st.info("Not enough data to generate timeline.")
        return
        
    df_intervals = pd.DataFrame(intervals)
    df_intervals["Timeline"] = "Session" # Constant for single-line chart
    
    # 2. Create Altair Chart
    # Color mapping
    domain = ["CODING", "RESEARCHING", "IDLE"]
    range_colors = ["#3b82f6", "#f97316", "#9ca3af"] # Blue, Orange, Gray
    
    chart = alt.Chart(df_intervals).mark_bar(size=30).encode(
        x=alt.X('Start', title='Time (seconds)'),
        x2='End',
        y=alt.Y('Timeline', title=None, axis=None),
        color=alt.Color('Activity', scale=alt.Scale(domain=domain, range=range_colors)),
        tooltip=['Activity', 'Start', 'End', 'Duration (s)']
    ).properties(
        height=80
    ).interactive()
    
    st.altair_chart(chart, use_container_width=True)



def render_clarity_section(df_events: pd.DataFrame) -> None:
    """
    Render the Clarity & Feedback section with clarity metrics over time, if present.
    """
    st.divider()
    st.header("Clarity & AI Feedback")
    st.caption(
        "This section evaluates how clearly the candidate explained their solution: "
        "coherence, use of terminology, and completeness. Higher scores mean the reasoning "
        "is easier to follow and more professional."
    )

    if df_events.empty:
        st.warning("No events found in this session.")
        return

    # Only keep CLARITY events that have at least one clarity field
    df_clarity = df_events[df_events["type"] == "CLARITY"].copy()
    df_clarity = df_clarity.dropna(
        subset=["coherence", "terminology", "completeness"],
        how="all",
    )

    if df_clarity.empty:
        st.info("No CLARITY events in this session.")
        return

    st.markdown(
        "- **Coherence**: logical flow of the explanation\n"
        "- **Terminology**: correct and precise technical vocabulary\n"
        "- **Completeness**: coverage of important steps and edge cases"
    )

    # Line chart over time
    st.subheader("Clarity over time")
    st.line_chart(
        df_clarity.set_index("ts")[
            ["coherence", "terminology", "completeness"]
        ],
        height=300,
    )

    # Latest clarity snapshot
    latest = df_clarity.sort_values("ts").iloc[-1]
    st.subheader("Latest clarity snapshot")

    c1, c2, c3 = st.columns(3)

    def fmt(value: Any) -> str:
        """
        Format numeric clarity value to a short string.
        """
        try:
            return f"{float(value):.2f}"
        except (TypeError, ValueError):
            return "N/A"

    c1.metric("Coherence", fmt(latest.get("coherence")))
    c2.metric("Terminology", fmt(latest.get("terminology")))
    c3.metric("Completeness", fmt(latest.get("completeness")))

    comment = latest.get("comment")
    if isinstance(comment, str) and comment.strip():
        st.markdown("#### Feedback on explanation")
        # Simple quote-style block for readability
        st.markdown(f"> {comment.strip()}")


# =========================
# Streamlit app entrypoint
# =========================

import subprocess
import sys

def init_session_state():
    if "user" not in st.session_state:
        st.session_state.user = None
    if "active_challenge" not in st.session_state:
        st.session_state.active_challenge = False
    if "view_mode" not in st.session_state:
        st.session_state.view_mode = "DASHBOARD" # DASHBOARD or RESULTS
    if "selected_challenge_key" not in st.session_state:
        st.session_state.selected_challenge_key = "secure_login"

# --- Challenge Definitions ---
CHALLENGES = {
    "secure_login": {
        "title": "🔥 Secure Login System (Advanced)",
        "description": "**Objective:** Implement a secure user authentication system.\n\n**Requirements:**\n- User registration and login\n- Password hashing (bcrypt)\n- JWT token generation\n- Input validation",
        "template": """def register_user(username, password):
    # Implement registration logic here
    pass

def login_user(username, password):
    # Implement login logic here
    pass
"""
    },
    "reverse_string": {
        "title": "String Reversal (Basic)",
        "description": "**Objective:** Write a function that reverses a string without using slice notation.\n\n**Time Limit:** 5 mins",
        "template": """def reverse_string(s):
    # Your code here
    pass
"""
    },
    "fizzbuzz": {
        "title": "FizzBuzz (Basic)",
        "description": "**Objective:** Print numbers 1 to n. Print 'Fizz' for multiples of 3, 'Buzz' for 5, 'FizzBuzz' for both.\n\n**Time Limit:** 5 mins",
        "template": """def fizzbuzz(n):
    # Your code here
    pass
"""
    },
    "palindrome": {
        "title": "Palindrome Checker (Basic)",
        "description": "**Objective:** Check if a string is a palindrome (reads the same forwards and backwards).\n\n**Time Limit:** 5 mins",
        "template": """def is_palindrome(s):
    # Your code here
    pass
"""
    }
}

def render_sidebar_account():
    with st.sidebar:
        st.divider()
        if st.session_state.user:
            # Logged in view
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown(
                    """
                    <div style="
                        width: 50px;
                        height: 50px;
                        border-radius: 50%;
                        background-color: #4CAF50;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: white;
                        font-weight: bold;
                        font-size: 20px;
                    ">
                    H7
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with col2:
                st.write(f"**{st.session_state.user['name']}**")
                st.caption("Senior Candidate")
            
            if st.button("Logout"):
                st.session_state.user = None
                st.session_state.active_challenge = False
                st.rerun()
        else:
            # Guest view
            st.info("Please login to start.")
            if st.button("👤 Login as Guest"):
                st.session_state.user = {"name": "Hacker_007", "role": "Candidate"}
                st.rerun()

def render_challenges_tab():
    """
    Render the Challenges tab where users can start a session and write code.
    """
    st.header("Available Challenges")
    
    # Challenge Selector
    challenge_keys = list(CHALLENGES.keys())
    # Create a mapping for display names
    display_map = {k: CHALLENGES[k]["title"] for k in challenge_keys}
    
    # If a session is active, lock the selection
    disabled = st.session_state.active_challenge
    
    selected_key = st.selectbox(
        "Choose a Challenge:",
        options=challenge_keys,
        format_func=lambda x: display_map[x],
        index=challenge_keys.index(st.session_state.selected_challenge_key),
        disabled=disabled
    )
    
    # Update state if changed and not locked
    if not disabled:
        st.session_state.selected_challenge_key = selected_key
        
    current_challenge = CHALLENGES[st.session_state.selected_challenge_key]

    # Challenge Card
    with st.container(border=True):
        st.subheader(current_challenge["title"])
        st.markdown(current_challenge["description"])
        
        # Check assignment status
        is_assigned = st.session_state.active_challenge
        user = st.session_state.user
        
        if is_assigned and user:
            st.info(f"✅ Assigned to **{user['name']}**")
            
            # --- CODE EDITOR ---
            st.divider()
            st.subheader("💻 Code Editor")
            
            # Default code template
            default_code = current_challenge["template"]
            code_input = st.text_area("Write your solution here:", value=default_code, height=300)
            
            if st.button("💾 Submit Solution", type="primary"):
                # Save code to file
                os.makedirs("submissions", exist_ok=True)
                filename = f"submissions/{user['name']}_solution.py"
                with open(filename, "w") as f:
                    f.write(code_input)
                
                # Signal backend to stop
                with open("STOP_SESSION", "w") as f:
                    f.write("STOP")
                
                st.success(f"Solution saved to {filename}!")
                st.info("Stopping session and generating report... (this may take up to 30 seconds)")
                
                # Poll for completion (max 30 seconds)
                import time
                max_retries = 30
                for i in range(max_retries):
                    time.sleep(1)
                    try:
                        with open(os.path.join("data", "session_log.json"), "r") as f:
                            data = json.load(f)
                        
                        # Check if session ended AND has final analysis
                        if data.get("ended_at") is not None:
                            # Also verify FINAL_ANALYSIS exists
                            has_final = any(e.get("type") == "FINAL_ANALYSIS" for e in data.get("events", []))
                            if has_final:
                                break
                    except:
                        pass
                
                # Update state to show results
                st.session_state.active_challenge = False
                st.session_state.view_mode = "RESULTS"
                st.rerun()

        else:
            col1, col2 = st.columns([1, 3])
            with col1:
                # Button logic
                btn_label = "🚀 Start Interview"
                btn_disabled = False
                
                if is_assigned:
                    btn_label = "⏳ In Progress..."
                    btn_disabled = True
                
                if st.button(btn_label, type="primary", use_container_width=True, disabled=btn_disabled):
                    if not user:
                        st.error("Please login first!")
                    else:
                        try:
                            # Clean up old session
                            # 1. Signal any running processes to stop
                            with open("STOP_SESSION", "w") as f:
                                f.write("STOP")
                            
                            # 2. Wait for old process to finish
                            import time
                            time.sleep(2)
                            
                            # 3. Delete old session log
                            log_path = os.path.join("data", "session_log.json")
                            if os.path.exists(log_path):
                                os.remove(log_path)
                            
                            # 4. Remove stop signal
                            if os.path.exists("STOP_SESSION"):
                                os.remove("STOP_SESSION")
                            
                            # Launch src/main.py in VISIBLE mode for debugging
                            if sys.platform == "win32":
                                subprocess.Popen(
                                    "start cmd /k python src/main.py", 
                                    shell=True
                                )
                            else:
                                subprocess.Popen(["python", "src/main.py"])
                            
                            st.session_state.active_challenge = True
                            st.session_state.view_mode = "CHALLENGE"
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Failed to start session: {e}")
            
            with col2:
                if not is_assigned:
                    st.caption("Clicking start will launch the AI backend silently. The editor will appear below.")
                else:
                    st.caption("Session is running.")

def render_results_view():
    """
    Render the final results after submission.
    """
    st.balloons()
    st.title("🎉 Challenge Completed!")
    
    # Load latest session log
    try:
        with open(os.path.join("data", "session_log.json"), "r") as f:
            data = json.load(f)
            
        user = st.session_state.user
        candidate_name = user['name'] if user else data.get("candidate_id", "Unknown")
        
        # Calculate duration
        start_time = data.get("started_at", 0)
        end_time = data.get("ended_at", 0)
        duration = 0
        if start_time and end_time:
            duration = end_time - start_time
        
        # Find Final Analysis
        final_transcript = "No transcript available."
        final_comment = "No analysis available."
        
        for event in data.get("events", []):
            if event["type"] == "FINAL_ANALYSIS":
                payload = event["payload"]
                final_transcript = payload.get("transcript", "No transcript found.")
                final_comment = payload.get("comment", "No comment found.")
        
        # Display Results
        col1, col2, col3 = st.columns(3)
        col1.metric("Candidate", candidate_name)
        col2.metric("Time Taken", f"{duration:.1f}s")
        col3.metric("Verdict", data["summary"].get("verdict", "PENDING"))
        
        st.divider()
        
        st.subheader("🗣️ Final Audio Transcript")
        st.info(f"\"{final_transcript}\"")
        
        st.subheader("🤖 AI Analysis")
        st.success(f"**Feedback:** {final_comment}")
        
        st.divider()
        
        if st.button("🔙 Back to Dashboard"):
            st.session_state.view_mode = "DASHBOARD"
            st.rerun()
            
    except Exception as e:
        st.error(f"Could not load results: {e}")

def render_audit_tab():
    """
    Render the Live Audit tab (existing dashboard logic).
    """
    # 1) Load session data
    try:
        session_data = load_session_log(os.path.join("data", "session_log.json"))
    except FileNotFoundError:
        st.warning("Waiting for session data... (Start a challenge first)")
        return
    except json.JSONDecodeError:
        st.warning("Reading session data...")
        return

    # 2) Transform events into a DataFrame
    events = session_data.get("events", [])
    df_events = events_to_df(events)

    # 3) Compute basic metrics
    metrics = compute_basic_metrics(session_data, df_events)

    # 4) Render main UI sections
    render_summary_section(metrics)
    render_timeline_section(df_events)
    render_clarity_section(df_events)
    
    # 5) Footer
    st.divider()
    st.caption("GlassBox – prototype dashboard for interviewing process audit.")

    # 6) Debug helpers
    with st.expander("Debug · raw session data"):
        st.json(session_data)

def render_leaderboard_tab():
    """
    Render the Leaderboard tab.
    """
    st.header("🏆 Hall of Fame")
    st.caption("Top performing candidates ranked by their Total Score (Hard + Soft skills).")
    
    lb = Leaderboard()
    if not lb.entries:
        st.info("No entries yet. Complete a challenge to get on the leaderboard!")
        return

    # Convert to DataFrame for display
    data = []
    for entry in lb.entries:
        data.append({
            "Rank": 0, # Placeholder
            "Name": entry.name,
            "Total Score": entry.total_score,
            "Hard Score": entry.hard_score,
            "Soft Score": entry.soft_score,
            "Timestamp": pd.to_datetime(entry.timestamp, unit='s').strftime('%Y-%m-%d %H:%M'),
            "_obj": entry # Hidden column for details
        })
    
    df = pd.DataFrame(data)
    df["Rank"] = range(1, len(df) + 1)
    
    # Display Main Table
    st.dataframe(
        df[["Rank", "Name", "Total Score", "Hard Score", "Soft Score", "Timestamp"]],
        column_config={
            "Total Score": st.column_config.ProgressColumn(
                "Total Score",
                help="Average of Hard and Soft scores",
                format="%.1f",
                min_value=0,
                max_value=100,
            ),
            "Hard Score": st.column_config.NumberColumn("Hard Score", format="%d"),
            "Soft Score": st.column_config.NumberColumn("Soft Score", format="%d"),
        },
        use_container_width=True,
        hide_index=True
    )
    
    st.divider()
    st.subheader("🔍 Submission Details")
    
    # Selection for details
    selected_name = st.selectbox(
        "Select a candidate to view details:",
        options=df["Name"].tolist(),
        index=0
    )
    
    if selected_name:
        # Find the entry object
        entry = next((item["_obj"] for item in data if item["Name"] == selected_name), None)
        
        if entry:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🤖 AI Overview")
                st.info(entry.ai_overview)
                
            with col2:
                st.markdown("### 💻 Code Submission")
                st.code(entry.code_content, language="python")

def main() -> None:
    """
    Main entrypoint for the Streamlit dashboard.
    """
    st.set_page_config(
        page_title="GlassBox Dashboard",
        page_icon="🧠",
        layout="wide",
    )
    
    # Initialize session state
    init_session_state()

    # Check View Mode
    if st.session_state.view_mode == "RESULTS":
        render_results_view()
        return

    st.title("GlassBox Candidate Session Dashboard")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["🎯 Challenges", "📊 Live Audit", "🏆 Leaderboard"])
    
    with tab1:
        render_challenges_tab()
        
    with tab2:
        render_audit_tab()

    with tab3:
        render_leaderboard_tab()

    # Sidebar
    with st.sidebar:
        # Render Account Widget
        render_sidebar_account()
        
        st.header("How to read this dashboard")
        st.markdown(
            "1. **Session Summary** – overall scores, verdict, and time distribution.\n"
            "2. **Activity Timeline** – when the candidate was CODING, RESEARCHING, or IDLE.\n"
            "3. **Clarity & AI Feedback** – explanation quality and the model's comment."
        )
        st.caption("Designed for demo purposes during megabrAIns Hackathon 2025.")

if __name__ == "__main__":
    main()
