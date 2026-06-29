import streamlit as st
import sqlite3
import hashlib
import base64
from datetime import datetime
import pandas as pd

st.set_page_config(
    page_title="PySquad Hub",
    page_icon="https://img.icons8.com/color/144/python.png",  # আসল পাইথন লোগো ট্যাব আইকন হিসেবে
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* স্ট্রিমলিটের ডিফল্ট হেডার-ফুটার হাইড করার জন্য */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* ব্যাকগ্রাউন্ড গ্লো অ্যানিমেশন (ধীরগতির অ্যাম্বিয়েন্ট মুভমেন্ট) */
    @keyframes ambientGlow {
        0% {
            background-position: 0px 0px, 0px 0px, 10% 20%, 90% 80%;
        }
        50% {
            background-position: 0px 0px, 0px 0px, 80% 80%, 20% 20%;
        }
        100% {
            background-position: 0px 0px, 0px 0px, 10% 20%, 90% 80%;
        }
    }
    
    /* ব্যাকগ্রাউন্ড ও প্রোগ্রামিং থিম কালার (IDE Grid with Animated Glow Effect) */
    .stApp {
        background-color: #0b0e14;
        background-image: 
            /* সূক্ষ্ম কোডিং গ্রিড প্যাটার্ন */
            linear-gradient(rgba(88, 166, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(88, 166, 255, 0.03) 1px, transparent 1px),
            /* অ্যাম্বিয়েন্ট কোডিং এনিমেটেড গ্লোয়িং লাইটস */
            radial-gradient(circle at center, rgba(31, 111, 235, 0.16) 0px, transparent 55%),
            radial-gradient(circle at center, rgba(139, 92, 246, 0.11) 0px, transparent 55%);
        background-size: 30px 30px, 30px 30px, 160% 160%, 160% 160%;
        background-attachment: fixed;
        animation: ambientGlow 25s ease-in-out infinite;
        color: #c9d1d9;
    }
    
    /* স্ট্রিমলিটের নিজস্ব বর্ডার কন্টেইনার এবং ফর্মকে সুন্দর কার্ডে রূপান্তর */
    div[data-testid="stVerticalBlockBorderWrapper"], div[data-testid="stForm"] {
        background-color: #161b22 !important;
        border: 1px solid #30363d !important;
        border-radius: 16px !important;
        padding: 24px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4) !important;
        margin-bottom: 20px !important;
    }
    
    /* টাইটেল এবং লোগো কন্টেইনার (মোবাইলে একদম এক লাইনে রাখার জন্য) */
    .logo-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        margin-bottom: 8px;
        margin-top: 20px;
        flex-wrap: nowrap; /* এক লাইনেই রাখবে, নিচে ভাঙবে না */
    }
    .logo-img {
        width: clamp(32px, 8vw, 54px); /* স্ক্রিন সাইজ অনুযায়ী লোগো ছোট-বড় হবে */
        height: clamp(32px, 8vw, 54px);
        filter: drop-shadow(0 0 8px rgba(88, 166, 255, 0.6));
        flex-shrink: 0;
    }
    .app-title {
        font-size: clamp(1.4rem, 6vw, 2.3rem); /* মোবাইলে ফন্ট সাইজ স্বয়ংক্রিয়ভাবে ছোট হয়ে এক লাইনে ফিট হবে */
        font-weight: 800;
        color: #58a6ff;
        margin: 0;
        font-family: 'Inter', sans-serif;
        text-shadow: 0 0 10px rgba(88, 166, 255, 0.2);
        line-height: 1.1;
        white-space: nowrap; /* কোনো অবস্থাতেই ভেঙে দ্বিতীয় লাইনে যাবে না */
    }
    .app-subtitle {
        font-size: clamp(0.7rem, 3.2vw, 1rem); /* সাবটাইটেলও মোবাইলে সংকুচিত হয়ে এক লাইনে থাকবে */
        color: #8b949e;
        text-align: center;
        margin-bottom: 25px;
        white-space: nowrap; /* কোনো অবস্থাতেই ভেঙে দ্বিতীয় লাইনে যাবে না */
    }
    .badge {
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
    }
    
    /* নোটিফিকেশন কার্ড ডিজাইন */
    .notif-card {
        background-color: #1c2128 !important;
        border-left: 4px solid #58a6ff !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
        margin-bottom: 12px !important;
    }
    
    /* বাটনের মডার্ন স্টাইল */
    div.stButton > button {
        background-color: #21262d !important;
        color: #c9d1d9 !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        width: 100% !important;
        padding: 10px 20px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #58a6ff !important;
        color: #0d1117 !important;
        box-shadow: 0 0 12px rgba(88, 166, 255, 0.4);
    }
    
    /* রেডিও বাটনের সুন্দর ডিজাইন */
    div[data-testid="stMarkdownContainer"] p {
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

DB_FILE = "learning_tracker.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # ইউজার টেবিল
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
        """)
        # ভিডিও টেবিল
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                task_desc TEXT,
                date_added TEXT NOT NULL
            )
        """)
        # ভিডিও ভিউ ট্র্যাকিং টেবিল
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS views (
                username TEXT,
                video_id INTEGER,
                viewed_at TEXT,
                PRIMARY KEY (username, video_id)
            )
        """)
        # টাস্ক সাবমিশন টেবিল
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                video_id INTEGER,
                screenshot TEXT, -- Base64 ফরম্যাটে ছবি
                submitted_at TEXT,
                FOREIGN KEY (video_id) REFERENCES videos(id)
            )
        """)
        # রিলোড ট্র্যাকিং এর জন্য সেশন টেবিল
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                username TEXT,
                token TEXT PRIMARY KEY,
                created_at TEXT
            )
        """)
        # নোটিফিকেশন সিস্টেম টেবিল
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT, -- 'ALL', 'admin' অথবা নির্দিষ্ট ইউজারনেম
                message TEXT,
                created_at TEXT
            )
        """)
        # নোটিফিকেশন রিড ট্র্যাকিং টেবিল (কার কার পড়া শেষ হয়েছে)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notification_reads (
                username TEXT,
                notification_id INTEGER,
                PRIMARY KEY (username, notification_id)
            )
        """)
        
        # ডিফল্ট অ্যাডমিন অ্যাকাউন্ট তৈরি
        admin_pass_hash = hashlib.sha256("Touhidul#20".encode()).hexdigest()
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                           ("admin", admin_pass_hash, "admin"))
        conn.commit()

init_db()

def add_notification(username, message):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO notifications (username, message, created_at)
            VALUES (?, ?, ?)
        """, (username, message, datetime.now().strftime("%Y-%m-%d %H:%M")))
        conn.commit()

def get_playable_url(url):
    if "youtu.be/" in url:
        video_id = url.split("youtu.be/")[1].split("?")[0]
        return f"https://www.youtube.com/watch?v={video_id}"
    elif "youtube.com/watch" in url:
        return url
    elif "youtube.com/embed/" in url:
        video_id = url.split("embed/")[1].split("?")[0]
        return f"https://www.youtube.com/watch?v={video_id}"
    elif "drive.google.com" in url:
        try:
            if "/file/d/" in url:
                file_id = url.split("/file/d/")[1].split("/")[0]
            elif "id=" in url:
                file_id = url.split("id=")[1].split("&")[0]
            else:
                return url
            return f"https://docs.google.com/uc?api=viewer&id={file_id}"
        except Exception:
            return url
    return url

def file_to_base64(uploaded_file):
    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        return base64.b64encode(file_bytes).decode("utf-8")
    return None

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "Home"
if "success_notification" not in st.session_state:
    st.session_state.success_notification = None
if "user_upload_success" not in st.session_state:
    st.session_state.user_upload_success = None

# Auto login via token
if not st.session_state.logged_in:
    query_params = st.query_params
    if "session_token" in query_params:
        token = query_params["session_token"]
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.username, u.role FROM sessions s 
                JOIN users u ON s.username = u.username 
                WHERE s.token = ?
            """, (token,))
            session_record = cursor.fetchone()
            if session_record:
                st.session_state.logged_in = True
                st.session_state.username = session_record["username"]
                st.session_state.role = session_record["role"]
            else:
                st.query_params.pop("session_token", None)

def login_user(username, password):
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_pw))
        user = cursor.fetchone()
        if user:
            st.session_state.logged_in = True
            st.session_state.username = user["username"]
            st.session_state.role = user["role"]
            
            token_string = f"{username}-{datetime.now().isoformat()}"
            token = hashlib.sha256(token_string.encode()).hexdigest()
            cursor.execute("INSERT OR REPLACE INTO sessions (username, token, created_at) VALUES (?, ?, ?)",
                           (username, token, datetime.now().isoformat()))
            conn.commit()
            
            st.query_params["session_token"] = token
            return True
    return False

def register_user(username, password):
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                           (username, hashed_pw, "user"))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False

st.markdown("""
<div class="logo-container">
    <img src="https://img.icons8.com/color/144/python.png" class="logo-img" alt="Python Logo">
    <h1 class="app-title">PySquad Hub</h1>
</div>
""", unsafe_allow_html=True)
st.markdown("<div class='app-subtitle'>সবাই মিলে একসাথে পাইথন শিখি ও প্রোগ্রেস ট্র্যাক করি</div>", unsafe_allow_html=True)

if not st.session_state.logged_in:
    with st.container(border=True):
        auth_mode = st.radio("আপনার অ্যাকশন সিলেক্ট করুন", ["লগইন করুন", "নতুন অ্যাকাউন্ট খুলুন"], horizontal=True)
        
        username_input = st.text_input("ইউজারনেম (Username)", placeholder="যেমন: Touhidul")
        password_input = st.text_input("পাসওয়ার্ড (Password)", type="password", placeholder="পাসওয়ার্ড লিখুন")
        
        if auth_mode == "লগইন করুন":
            if st.button("ড্যাশবোর্ডে প্রবেশ করুন 🚀"):
                if username_input and password_input:
                    if login_user(username_input, password_input):
                        st.success(f"স্বাগতম, {st.session_state.username}!")
                        st.rerun()
                    else:
                        st.error("ভুল ইউজারনেম অথবা পাসওয়ার্ড! আবার চেষ্টা করুন।")
                else:
                    st.warning("দয়া করে সবগুলো ঘর পূরণ করুন।")
        else:
            if st.button("রেজিস্ট্রেশন সম্পন্ন করুন ✨"):
                if username_input and password_input:
                    if len(password_input) < 4:
                        st.error("পাসওয়ার্ড অন্তত ৪ অক্ষরের হতে হবে।")
                    elif register_user(username_input, password_input):
                        st.success("অ্যাকাউন্ট তৈরি সফল হয়েছে! এখন লগইন করুন।")
                    else:
                        st.error("এই ইউজারনেমটি ইতিমধ্যে ব্যবহৃত হয়েছে। অন্য নাম দিন।")
                else:
                    st.warning("দয়া করে সবগুলো ঘর পূরণ করুন।")

else:
    st.markdown("---")
    nav_cols = st.columns(4 if st.session_state.role == "admin" else 3)
    
    with nav_cols[0]:
        if st.button("🎬 ভিডিওসমূহ"): st.session_state.current_tab = "Home"
    with nav_cols[1]:
        if st.button("📊 ট্র্যাকার"): st.session_state.current_tab = "Tracker"
    with nav_cols[2]:
        if st.button("🔓 লগআউট"):
            token = st.query_params.get("session_token")
            if token:
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM sessions WHERE token = ?", (token,))
                    conn.commit()
            st.query_params.pop("session_token", None)
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.role = None
            st.rerun()
    if st.session_state.role == "admin":
        with nav_cols[3]:
            if st.button("⚙️ অ্যাডমিন"): st.session_state.current_tab = "Admin"

    username = st.session_state.username
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if username == 'admin':
            cursor.execute("""
                SELECT n.* FROM notifications n
                LEFT JOIN notification_reads nr ON n.id = nr.notification_id AND nr.username = 'admin'
                WHERE (n.username = 'admin' OR n.username = 'ALL') AND nr.notification_id IS NULL
                ORDER BY n.id DESC
            """)
        else:
            cursor.execute("""
                SELECT n.* FROM notifications n
                LEFT JOIN notification_reads nr ON n.id = nr.notification_id AND nr.username = ?
                WHERE (n.username = ? OR n.username = 'ALL') AND nr.notification_id IS NULL
                ORDER BY n.id DESC
            """, (username, username))
        unread_notifs = cursor.fetchall()
        
    if unread_notifs:
        st.markdown("### 🔔 নতুন নোটিফিকেশন")
        for notif in unread_notifs:
            with st.container(border=True):
                st.markdown(f"<div class='notif-card'>{notif['message']}</div>", unsafe_allow_html=True)
                st.caption(f"সময়: {notif['created_at']}")
                if st.button("পঠিত হিসেবে মার্ক করুন ✓", key=f"read_notif_{notif['id']}"):
                    with get_db_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT OR IGNORE INTO notification_reads (username, notification_id)
                            VALUES (?, ?)
                        """, (st.session_state.username, notif['id']))
                        conn.commit()
                    st.rerun()
        st.markdown("---")

    # ----------------- পেজ ১: ভিডিও পোর্টাল (HOME) -----------------
    if st.session_state.current_tab == "Home":
        st.subheader("আপনার আজকের ক্লাসের ভিডিও")
        
        # সফল স্ক্রিনশট আপলোড সাকসেস মেসেজ শো করা
        if st.session_state.user_upload_success:
            st.success(st.session_state.user_upload_success)
            st.session_state.user_upload_success = None
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM videos ORDER BY id ASC")
            all_videos = cursor.fetchall()
            
        if not all_videos:
            st.info("এখনো কোনো ভিডিও আপলোড করা হয়নি। গ্রুপ লিডারকে ভিডিও দেওয়ার জন্য বলুন!")
        else:
            for idx, vid in enumerate(all_videos):
                vid_id = vid["id"]
                with st.container(border=True):
                    st.markdown(f"<h3>ভিডিও #{idx+1}: {vid['title']}</h3>", unsafe_allow_html=True)
                    
                    with get_db_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT * FROM views WHERE username = ? AND video_id = ?", 
                                       (st.session_state.username, vid_id))
                        watched = cursor.fetchone() is not None
                    
                    if watched:
                        st.markdown("<span class='badge' style='background-color:#1f6feb;'>দেখেছি ✅</span>", unsafe_allow_html=True)
                    else:
                        st.markdown("<span class='badge' style='background-color:#da3633;'>দেখা হয়নি ❌</span>", unsafe_allow_html=True)
                    
                    st.write("")
                    
                    playable_link = get_playable_url(vid["url"])
                    try:
                        st.video(playable_link)
                    except Exception:
                        st.error("ভিডিওটি লোড করা যাচ্ছে না। অনুগ্রহ করে সঠিক লিংক ব্যবহার করুন।")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if not watched:
                            if st.button("দেখা শেষ করলাম 👀", key=f"watch_btn_{vid_id}"):
                                with get_db_connection() as conn:
                                    cursor = conn.cursor()
                                    cursor.execute("INSERT OR IGNORE INTO views (username, video_id, viewed_at) VALUES (?, ?, ?)",
                                                   (st.session_state.username, vid_id, datetime.now().strftime("%Y-%m-%d %H:%M")))
                                    conn.commit()
                                st.success("ভিডিও দেখা সফলভাবে সেভ হয়েছে!")
                                st.rerun()
                    with col2:
                        with st.expander("📤 স্ক্রিনশট জমা দিন (একসাথে ৫টি পর্যন্ত)"):
                            up_files = st.file_uploader(
                                "আপনার প্র্যাকটিসের স্ক্রিনশট সিলেক্ট করুন (একের অধিক সিলেক্ট করতে পারেন)", 
                                type=["png", "jpg", "jpeg"], 
                                accept_multiple_files=True,
                                key=f"up_{vid_id}"
                            )
                            if st.button("টাস্ক সাবমিট করুন 🚀", key=f"sub_btn_{vid_id}"):
                                if up_files:
                                    if len(up_files) > 5:
                                        st.error("⚠️ দুঃখিত, আপনি একসাথে সর্বোচ্চ ৫টি স্ক্রিনশট আপলোড করতে পারবেন।")
                                    else:
                                        with get_db_connection() as conn:
                                            cursor = conn.cursor()
                                            for single_file in up_files:
                                                b64_img = file_to_base64(single_file)
                                                cursor.execute("""
                                                    INSERT INTO submissions (username, video_id, screenshot, submitted_at) 
                                                    VALUES (?, ?, ?, ?)
                                                """, (st.session_state.username, vid_id, b64_img, datetime.now().strftime("%Y-%m-%d %H:%M")))
                                            
                                            cursor.execute("INSERT OR IGNORE INTO views (username, video_id, viewed_at) VALUES (?, ?, ?)",
                                                           (st.session_state.username, vid_id, datetime.now().strftime("%Y-%m-%d %H:%M")))
                                            conn.commit()
                                        
                                        # অ্যাডমিন প্যানেলে রিয়েল-টাইম নোটিফিকেশন পাঠানো
                                        add_notification('admin', f"📥 **{st.session_state.username}** ভিডিও '`{vid['title']}`' এর {len(up_files)}টি প্র্যাকটিস স্ক্রিনশট সাবমিট করেছে!")
                                        
                                        # ইউজারের জন্য সফল আপলোডের নোটিফিকেশন সেট
                                        st.session_state.user_upload_success = f"🎉 সফলভাবে আপনার {len(up_files)}টি প্র্যাকটিস স্ক্রিনশট আপলোড হয়েছে!"
                                        st.rerun()
                                else:
                                    st.error("দয়া করে কমপক্ষে একটি প্র্যাকটিস স্ক্রিনশট সিলেক্ট করুন।")

    # ----------------- পেজ ২: প্রোগ্রেস ট্র্যাকার (TRACKER) -----------------
    elif st.session_state.current_tab == "Tracker":
        st.subheader("গ্রুপের বন্ধুদের কাজের ট্র্যাকিং")
        
        with get_db_connection() as conn:
            df_users = pd.read_sql_query("SELECT username FROM users WHERE role != 'admin'", conn)
            df_vids = pd.read_sql_query("SELECT id, title FROM videos", conn)
            df_subs = pd.read_sql_query("SELECT username, video_id FROM submissions", conn)
            
        if df_users.empty:
            st.info("এখনো কোনো মেম্বার রেজিস্ট্রেশন করেনি।")
        elif df_vids.empty:
            st.info("ট্র্যাক করার জন্য এখনো কোনো ভিডিও আপলোড করা হয়নি।")
        else:
            st.write("### 📉 কার কার কোন টাস্ক বাদ আছে?")
            for _, u in df_users.iterrows():
                user = u["username"]
                completed_ids = set(df_subs[df_subs["username"] == user]["video_id"].tolist())
                all_ids = set(df_vids["id"].tolist())
                missing_ids = all_ids - completed_ids
                
                with st.container(border=True):
                    st.markdown(f"**👤 মেম্বার:** `{user}`")
                    if not missing_ids:
                        st.markdown("<span class='badge' style='background-color:#238636;'>সবগুলো টাস্ক সম্পন্ন করেছে! 🔥</span>", unsafe_allow_html=True)
                    else:
                        missing_labels = []
                        for m_id in missing_ids:
                            matching_rows = df_vids[df_vids["id"] == m_id]
                            if not matching_rows.empty:
                                idx = matching_rows.index[0] + 1
                                missing_labels.append(f"ভিডিও {idx}")
                        st.markdown(f"🔴 **বাকি আছে:** {', '.join(missing_labels)}")
            
            st.write("### 📸 সবার জমা দেওয়া প্র্যাকটিস স্ক্রিনশটসমূহ")
            
            # মেম্বারদের তালিকা সংগ্রহ ফিল্টারের জন্য
            member_names = list(df_users["username"].unique())
            member_filter = st.selectbox(
                "🔍 মেম্বার অনুযায়ী স্ক্রিনশট ফিল্টার করুন:", 
                ["সবাই (All Members)"] + member_names
            )
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                if member_filter == "সবাই (All Members)":
                    cursor.execute("""
                        SELECT s.id as sub_id, s.username, s.submitted_at, s.screenshot, v.title, v.id as vid_id 
                        FROM submissions s 
                        JOIN videos v ON s.video_id = v.id 
                        ORDER BY s.id DESC
                    """)
                else:
                    cursor.execute("""
                        SELECT s.id as sub_id, s.username, s.submitted_at, s.screenshot, v.title, v.id as vid_id 
                        FROM submissions s 
                        JOIN videos v ON s.video_id = v.id 
                        WHERE s.username = ?
                        ORDER BY s.id DESC
                    """, (member_filter,))
                all_subs = cursor.fetchall()
                
            if not all_subs:
                st.info("নির্বাচিত মেম্বারের কোনো স্ক্রিনশট পাওয়া যায়নি।")
            else:
                for sub in all_subs:
                    with st.container(border=True):
                        st.markdown(f"👤 **{sub['username']}** স্ক্রিনশট জমা দিয়েছে - **ভিডিও: `{sub['title']}`**-এর জন্য")
                        st.caption(f"জমা দেওয়ার সময়: {sub['submitted_at']}")
                        
                        img_data = sub["screenshot"]
                        try:
                            st.image(base64.b64decode(img_data), use_column_width=True)
                        except Exception:
                            st.error("ছবিটি লোড করতে সমস্যা হচ্ছে।")
                            
                        if st.session_state.role == "admin":
                            if st.button("🗑️ ছবি ডিলিট করুন (সাইলেন্টলি)", key=f"del_screenshot_{sub['sub_id']}"):
                                with get_db_connection() as conn:
                                    cursor = conn.cursor()
                                    cursor.execute("DELETE FROM submissions WHERE id = ?", (sub["sub_id"],))
                                    conn.commit()
                                st.success("ছবিটি সফলভাবে মুছে ফেলা হয়েছে!")
                                st.rerun()

    # ----------------- পেজ ৩: অ্যাডমিন প্যানেল (ADMIN) -----------------
    elif st.session_state.current_tab == "Admin" and st.session_state.role == "admin":
        st.subheader("গ্রুপ লিডার কন্ট্রোল প্যানেল (অ্যাডমিন)")
        
        if st.session_state.success_notification:
            st.success(st.session_state.success_notification)
            st.session_state.success_notification = None
        
        admin_action = st.radio(
            "মডিউল সিলেক্ট করুন:", 
            ["📤 নতুন ভিডিও দিন", "👁️ ভিউ ট্র্যাকিং", "🗑️ ভিডিও মুছুন", "👥 মেম্বার ম্যানেজমেন্ট"], 
            horizontal=True
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # অ্যাকশন ১: নতুন ভিডিও আপলোড
        if admin_action == "📤 নতুন ভিডিও দিন":
            with st.container(border=True):
                st.write("### 🎬 নতুন ভিডিও আপলোড করুন")
                v_title = st.text_input("ভিডিওর শিরোনাম (যেমন: Python List Tutorial)", placeholder="শিরোনাম লিখুন...")
                v_url = st.text_input("ইউটিউব/ড্রাইভ ভিডিও লিংক", placeholder="যেমন: https://www.youtube.com/watch?v=...")
                
                if st.button("ভিডিও পাবলিশ করুন 📣"):
                    if v_title and v_url:
                        with get_db_connection() as conn:
                            cursor = conn.cursor()
                            cursor.execute("INSERT INTO videos (title, url, task_desc, date_added) VALUES (?, ?, ?, ?)",
                                           (v_title, v_url, None, datetime.now().strftime("%Y-%m-%d")))
                            conn.commit()
                        
                        # নতুন ভিডিও আপলোডের নোটিফিকেশন ব্রডকাস্ট করুন
                        add_notification('ALL', f"📣 নতুন ভিডিও আপলোড করা হয়েছে: **{v_title}**! ড্যাশবোর্ডে গিয়ে ভিডিওটি দেখে টাস্ক কমপ্লিট করো।")
                        
                        st.session_state.success_notification = f"🎉 সফলভাবে ভিডিও আপলোড হয়েছে: {v_title}"
                        st.rerun()
                    else:
                        st.error("ভিডিওর শিরোনাম এবং লিংক অবশ্যই দিতে হবে!")
        
        # অ্যাকশন ২: ভিউ ট্র্যাকিং
        elif admin_action == "👁️ ভিউ ট্র্যাকিং":
            with st.container(border=True):
                st.write("### 👁️ কোন ভিডিও কে কে দেখেছে দেখুন")
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT id, title FROM videos")
                    vids_list = cursor.fetchall()
                    
                if vids_list:
                    selected_vid = st.selectbox("ভিডিও সিলেক্ট করুন", 
                                                options=[v["id"] for v in vids_list], 
                                                format_func=lambda x: f"ভিডিও {x} - " + [v["title"] for v in vids_list if v["id"] == x][0])
                    
                    with get_db_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            SELECT username, viewed_at FROM views 
                            WHERE video_id = ?
                        """, (selected_vid,))
                        viewers = cursor.fetchall()
                        
                    if viewers:
                        st.success(f"মোট ভিউয়ার্স সংখ্যা: {len(viewers)} জন")
                        for vw in viewers:
                            st.write(f"- 👤 **{vw['username']}** (দেখেছে: {vw['viewed_at']})")
                    else:
                        st.warning("এখনো কেউ এই ভিডিওটি দেখেছে হিসেবে মার্ক করেনি।")
                else:
                    st.info("ভিউয়ার্স ট্র্যাক করার জন্য আগে ভিডিও আপলোড করুন।")
            
        elif admin_action == "🗑️ ভিডিও মুছুন":
            with st.container(border=True):
                st.write("### 🗑️ ভিডিও ডিলিট ম্যানেজমেন্ট")
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT id, title, date_added FROM videos ORDER BY id ASC")
                    all_vids_to_del = cursor.fetchall()
                    
                if not all_vids_to_del:
                    st.info("মুছে ফেলার মতো কোনো ভিডিও পাওয়া যায়নি।")
                else:
                    for v_del in all_vids_to_del:
                        col_vid_info, col_vid_act = st.columns([3, 1])
                        with col_vid_info:
                            st.write(f"🎬 **{v_del['title']}** (তারিখ: {v_del['date_added']})")
                        with col_vid_act:
                            if st.button("🗑️ মুছুন", key=f"del_v_{v_del['id']}"):
                                with get_db_connection() as conn:
                                    cursor = conn.cursor()
                                    cursor.execute("DELETE FROM videos WHERE id = ?", (v_del["id"],))
                                    cursor.execute("DELETE FROM views WHERE video_id = ?", (v_del["id"],))
                                    cursor.execute("DELETE FROM submissions WHERE video_id = ?", (v_del["id"],))
                                    conn.commit()
                                st.success("ভিডিওটি সফলভাবে মুছে ফেলা হয়েছে!")
                                st.rerun()
                        st.markdown("---")

        elif admin_action == "👥 মেম্বার ম্যানেজমেন্ট":
            st.write("### 👥 গ্রুপ মেম্বার ম্যানেজমেন্ট ও কন্ট্রোল")
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT username FROM users WHERE role != 'admin' ORDER BY username ASC")
                members = cursor.fetchall()
                
            if not members:
                st.info("এখনো কোনো মেম্বার রেজিস্ট্রেশন করেনি।")
            else:
                for member in members:
                    m_username = member["username"]
                    with st.container(border=True):
                        st.markdown(f"**👤 মেম্বার:** `{m_username}`")
                        
                        col_rem, col_del = st.columns(2)
                        with col_rem:
                            # রিমাইন্ডার পাঠানোর সাব-সেকশন
                            with st.expander(f"🔔 {m_username} কে রিমাইন্ডার দিন"):
                                rem_message = st.text_input("রিমাইন্ডার মেসেজটি লিখুন", 
                                                            placeholder="যেমন: তোমার ভিডিওর প্র্যাকটিস কাজটি এখনো বাকি আছে!",
                                                            key=f"rem_input_{m_username}")
                                if st.button("রিমাইন্ডার পাঠান 🚀", key=f"send_rem_btn_{m_username}"):
                                    if rem_message:
                                        add_notification(m_username, f"⚠️ **গ্রুপ লিডার রিমাইন্ডার:** {rem_message}")
                                        st.success(f"{m_username}-এর কাছে রিমাইন্ডার সফলভাবে পাঠানো হয়েছে!")
                                    else:
                                        st.error("মেসেজ খালি রাখা যাবে না!")
                        with col_del:
                            # মেম্বার সম্পূর্ণ রিমুভ করার বাটন
                            if st.button(f"🗑️ {m_username} কে রিমুভ করুন", key=f"del_member_btn_{m_username}"):
                                with get_db_connection() as conn:
                                    cursor = conn.cursor()
                                    cursor.execute("DELETE FROM users WHERE username = ?", (m_username,))
                                    cursor.execute("DELETE FROM views WHERE username = ?", (m_username,))
                                    cursor.execute("DELETE FROM submissions WHERE username = ?", (m_username,))
                                    cursor.execute("DELETE FROM sessions WHERE username = ?", (m_username,))
                                    cursor.execute("DELETE FROM notification_reads WHERE username = ?", (m_username,))
                                    cursor.execute("DELETE FROM notifications WHERE username = ?", (m_username,))
                                    conn.commit()
                                st.success(f"সাফল্যের সাথে মেম্বার `{m_username}` এবং তার সমস্ত ডেটা রিমুভ করা হয়েছে!")
                                st.rerun()
