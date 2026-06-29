import streamlit as st
import sqlite3
import datetime
import hashlib
import json

# --- CONFIGURATION & PAGE SETUP ---
st.set_page_config(
    page_title="Shared Learning Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_FILE = "local_learning_tracker.db"

# --- CUSTOM CSS FOR RESPONSIVENESS & FULL-SCREEN TOGGLE ---
st.markdown("""
<style>
    /* Responsive grid and padding tweaks */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    /* Simple Card styling for videos */
    .video-card {
        background-color: rgba(151, 166, 195, 0.1);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        border: 1px solid rgba(151, 166, 195, 0.2);
    }
    /* Dynamic full-screen style if toggled */
    .fullscreen-element {
        width: 100% !important;
        max-width: 100% !important;
    }
</style>
""", unsafe_allow_html=True)

# --- DATABASE INITIALIZATION ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Users table (Plain/MD5 hash for simplicity as requested, Admin default injected)
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL)''')
    
    # Videos table
    c.execute('''CREATE TABLE IF NOT EXISTS videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    description TEXT,
                    task_desc TEXT,
                    date_added TEXT)''')
    
    # Submissions table
    c.execute('''CREATE TABLE IF NOT EXISTS submissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    video_id INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    submission_text TEXT,
                    timestamp TEXT,
                    FOREIGN KEY(video_id) REFERENCES videos(id))''')
    
    # Insert default admin if not exists (Password: adminpassword)
    # Using SHA-256 for a baseline security standard
    admin_pw_hash = hashlib.sha256("adminpassword".encode()).hexdigest()
    try:
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                  ("admin", admin_pw_hash, "admin"))
    except sqlite3.IntegrityError:
        pass # Admin already exists
        
    conn.commit()
    conn.close()

init_db()

# --- DATABASE HELPER FUNCTIONS ---
def run_query(query, params=(), fetch="all"):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(query, params)
    if fetch == "all":
        result = c.fetchall()
    elif fetch == "one":
        result = c.fetchone()
    else:
        result = None
    conn.commit()
    conn.close()
    return result

# --- LOCALSTORAGE STATE SYNCHRONIZATION WORKAROUND ---
# Injects JavaScript to synchronize Streamlit session state with browser LocalStorage
def sync_local_storage():
    if "user_synced" not in st.session_state:
        st.session_state.user_synced = False

    # JS snippet to get/set localStorage values cleanly
    st.components.v1.html(
        f"""
        <script>
        const setStreamlitState = (key, value) => {{
            window.parent.postMessage({{
                type: 'streamlit:set_widget_value',
                key: key,
                value: value
            }}, '*');
        }};
        
        // Read local storage on initial run
        let localUser = localStorage.getItem('learning_portal_user');
        let localRole = localStorage.getItem('learning_portal_role');
        
        if (localUser && !"{st.session_state.get('username', '')}") {{
             window.parent.postMessage({{type: 'streamlit:set_user', username: localUser, role: localRole}}, '*');
        }}
        </script>
        """,
        height=0,
    )

# --- SESSION STATE INITIALIZATION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = None
if "fullscreen" not in st.session_state:
    st.session_state.fullscreen = False

# --- LOGOUT FUNCTION ---
def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.markdown("<script>localStorage.clear();</script>", unsafe_allow_html=True)
    st.rerun()

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🎓 Learning Portal")

if st.session_state.logged_in:
    st.sidebar.subheader(f"Welcome, {st.session_state.username}!")
    st.sidebar.info(f"Role: {st.session_state.role.capitalize()}")
    
    # Standard navigation mapping
    pages = ["Dashboard / Videos", "Progress & Leaderboard"]
    if st.session_state.role == "admin":
        pages.append("Admin Panel")
        
    page_selection = st.sidebar.radio("Go to Page:", pages)
    
    if st.sidebar.button("Log Out", use_container_width=True):
        logout()
else:
    page_selection = "Login / Register"
    st.sidebar.warning("Please Log In to access pages.")

st.sidebar.markdown("---")
st.sidebar.caption("💡 Hosted Free on Streamlit Community Cloud with a local SQLite engine.")

# --- PAGE 1: LOGIN & REGISTRATION ---
if page_selection == "Login / Register":
    st.title("🔐 Portal Authentication")
    
    tab1, tab2 = st.tabs(["Login", "Register New Account"])
    
    with tab1:
        st.subheader("Login to Your Dashboard")
        login_user = st.text_input("Username", key="login_user_input").strip()
        login_pass = st.text_input("Password", type="password", key="login_pass_input")
        
        if st.button("Sign In", type="primary"):
            hashed_pw = hashlib.sha256(login_pass.encode()).hexdigest()
            user_record = run_query("SELECT username, role FROM users WHERE username = ? AND password = ?", 
                                    (login_user, hashed_pw), fetch="one")
            
            if user_record:
                st.session_state.logged_in = True
                st.session_state.username = user_record[0]
                st.session_state.role = user_record[1]
                
                # HTML injection workaround to force write token state into localStorage safely
                st.markdown(f"""
                    <script>
                        localStorage.setItem('learning_portal_user', '{user_record[0]}');
                        localStorage.setItem('learning_portal_role', '{user_record[1]}');
                    </script>
                """, unsafe_allow_html=True)
                
                st.success(f"Success! Welcome back, {user_record[0]}.")
                st.rerun()
            else:
                st.error("Invalid Username or Password. Please try again.")
                
    with tab2:
        st.subheader("Create a New Account")
        reg_user = st.text_input("Choose Username", key="reg_user_input").strip()
        reg_pass = st.text_input("Choose Password", type="password", key="reg_pass_input")
        reg_pass_conf = st.text_input("Confirm Password", type="password", key="reg_pass_conf_input")
        
        if st.button("Register Account"):
            if not reg_user or not reg_pass:
                st.error("Fields cannot be empty.")
            elif reg_pass != reg_pass_conf:
                st.error("Passwords do not match.")
            else:
                hashed_reg_pw = hashlib.sha256(reg_pass.encode()).hexdigest()
                try:
                    run_query("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                              (reg_user, hashed_reg_pw, "student"), fetch="none")
                    st.success("Account created successfully! You can now log in above.")
                except sqlite3.IntegrityError:
                    st.error("Username already taken. Please try another one.")

# --- PAGE 2: DASHBOARD / VIDEO PORTAL (STUDENT VIEW) ---
elif page_selection == "Dashboard / Videos":
    st.title("📺 Learning Hub Portal")
    
    # Toggle Distraction-free / Full-Width mode dynamically via Session State Toggle
    col_title, col_toggle = st.columns([3, 1])
    with col_toggle:
        if st.checkbox("🎯 Toggle Full-Screen Focus Mode", value=st.session_state.fullscreen):
            st.session_state.fullscreen = True
            st.markdown("<style>.main .block-container { max-width: 100% !important; padding-left: 1rem; padding-right: 1rem; }</style>", unsafe_allow_html=True)
        else:
            st.session_state.fullscreen = False

    videos = run_query("SELECT id, title, url, description, task_desc FROM videos ORDER BY id DESC")
    
    if not videos:
        st.info("No educational videos have been published yet. Check back soon!")
    else:
        for vid_id, title, url, desc, task_desc in videos:
            st.markdown(f"""<div class='video-card'><h3>🎥 {title}</h3><p><i>{desc}</i></p></div>""", unsafe_allow_html=True)
            
            # Responsive video component embedding
            try:
                st.video(url)
            except Exception as e:
                st.warning(f"Could not load streaming player for this URL format. Direct link: [Watch Here]({url})")
                
            # Task & Assignment Box Section
            with st.expander("📝 View Associated Assignment / Task", expanded=True):
                st.markdown(f"**Task Requirements:**\n{task_desc}")
                
                # Check for existing submission
                existing_sub = run_query("SELECT submission_text, timestamp FROM submissions WHERE username = ? AND video_id = ?", 
                                         (st.session_state.username, vid_id), fetch="one")
                
                if existing_sub:
                    st.success(f"✓ You submitted a task on {existing_sub[1]}")
                    st.info(f"**Your Previous Record:** {existing_sub[0]}")
                
                # Submission Form
                with st.form(key=f"sub_form_{vid_id}"):
                    sub_text = st.text_area("Paste your GitHub repository link, code output, or text notes here:", placeholder="https://github.com/...")
                    submit_btn = st.form_submit_button("Submit Assignment")
                    
                    if submit_btn:
                        if not sub_text.strip():
                            st.error("Submission text cannot be blank.")
                        else:
                            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            if existing_sub:
                                # Update entry
                                run_query("UPDATE submissions SET submission_text = ?, timestamp = ? WHERE username = ? AND video_id = ?",
                                          (sub_text, now, st.session_state.username, vid_id), fetch="none")
                            else:
                                # New entry
                                run_query("INSERT INTO submissions (username, video_id, status, submission_text, timestamp) VALUES (?, ?, ?, ?, ?)",
                                          (st.session_state.username, vid_id, "Completed", sub_text, now), fetch="none")
                            st.success("Assignment updated and saved successfully!")
                            st.rerun()
            st.markdown("---")

# --- PAGE 3: PROGRESS TRACKER & LEADERBOARD (PUBLIC VIEW) ---
elif page_selection == "Progress & Leaderboard":
    st.title("🏆 Group Progress & Dashboard Monitoring")
    
    users = [u[0] for u in run_query("SELECT username FROM users WHERE role = 'student'")]
    all_videos = run_query("SELECT id, title FROM videos")
    
    # 1. Missing Tasks Core Logic Analysis
    st.subheader("⚠️ Missing Assignments Warning Desk")
    
    missing_data = []
    for user in users:
        user_subs = [s[0] for s in run_query("SELECT video_id FROM submissions WHERE username = ?", (user,))]
        missing_tasks = []
        for vid_id, vid_title in all_videos:
            if vid_id not in user_subs:
                missing_tasks.append(vid_title)
                
        status_string = ", ".join(missing_tasks) if missing_tasks else "🎉 All Tasks Completed!"
        missing_data.append({"User / Student": user, "Missing Content Assignments": status_string})
        
    st.table(missing_data)
    
    # 2. Raw Submissions Review Stream Feed
    st.markdown("---")
    st.subheader("👀 Peer Review Feed (All Group Submissions)")
    
    raw_feed = run_query("""
        SELECT s.username, v.title, s.submission_text, s.timestamp 
        FROM submissions s 
        JOIN videos v ON s.video_id = v.id 
        ORDER BY s.timestamp DESC
    """)
    
    if not raw_feed:
        st.info("No submissions processed across the group yet.")
    else:
        for student, v_title, text_content, time_stamp in raw_feed:
            with st.chat_message("user"):
                st.markdown(f"**{student}** turned in workspace for *{v_title}*")
                st.caption(f"Submitted on: {time_stamp}")
                st.code(text_content, language="markdown")

# --- PAGE 4: ADMIN PANEL ---
elif page_selection == "Admin Panel" and st.session_state.role == "admin":
    st.title("🛠️ Administrator Control Panel")
    
    tab_vid, tab_users = st.tabs(["📤 Publish Video Content", "👥 Manage Users Workspace"])
    
    with tab_vid:
        st.subheader("Upload & Broadcast New Task Module")
        with st.form("admin_video_form"):
            v_title = st.text_input("Video Title / Topic Title")
            v_url = st.text_input("Video Stream URL (YouTube, Drive, etc.)")
            v_desc = st.text_area("Brief Overview / Subtext Description")
            v_task = st.text_area("Detailed Assignment Task Instructions")
            
            submit_video = st.form_submit_button("Publish Course Module")
            
            if submit_video:
                if not v_title or not v_url or not v_task:
                    st.error("Title, Video Link, and Assignment Data fields are mandatory.")
                else:
                    today_str = datetime.date.today().isoformat()
                    run_query("INSERT INTO videos (title, url, description, task_desc, date_added) VALUES (?, ?, ?, ?, ?)",
                              (v_title, v_url, v_desc, v_task, today_str), fetch="none")
                    st.success(f"Successfully published: '{v_title}'!")
                    st.rerun()
                    
    with tab_users:
        st.subheader("Registered Peer Network Profiles")
        user_profiles = run_query("SELECT id, username, role FROM users")
        
        # Format into clean readable structured layout
        import pandas as pd
        df_users = pd.DataFrame(user_profiles, columns=["Database ID", "Username Account", "System Role Permission"])
        st.dataframe(df_users, use_container_width=True)
