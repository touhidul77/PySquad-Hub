import streamlit as st
import sqlite3
import hashlib
import uuid
import pandas as pd
from datetime import datetime

# পেজ কনফিগারেশন
st.set_page_config(
    page_title="PySquad Hub",
    page_icon="https://img.icons8.com/color/144/python.png",
    layout="centered"
)

# ডাটাবেস কানেকশন
def get_db_connection():
    conn = sqlite3.connect('pysquad.db', check_same_thread=False)
    return conn

# টেবিল তৈরি (যদি না থাকে)
def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS videos 
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, url TEXT, date_added DATETIME)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS sessions 
                          (username TEXT PRIMARY KEY, token TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                          (username TEXT PRIMARY KEY, password TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS views 
                          (username TEXT, video_id INTEGER)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS submissions 
                          (username TEXT, content TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS notifications 
                          (username TEXT, message TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS notification_reads 
                          (username TEXT, notification_id INTEGER)''')
        conn.commit()

init_db()

# সেশন এবং লগইন ম্যানেজমেন্ট
def check_persistent_login():
    query_params = st.query_params
    token = query_params.get("session_token")
    if token:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM sessions WHERE token = ?", (token,))
            user = cursor.fetchone()
            if user:
                st.session_state.logged_in = True
                st.session_state.username = user[0]

# ভিডিও সিরিয়াল (Latest First) দেখার ফাংশন
def display_videos():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT title, url FROM videos ORDER BY id DESC")
        videos = cursor.fetchall()
        
    if not videos:
        st.info("কোনো ভিডিও পাওয়া যায়নি।")
    else:
        for title, url in videos:
            st.subheader(title)
            st.video(url)

# অ্যাডমিন প্যানেল বা মেম্বার ম্যানেজমেন্ট ফাংশন (আপনার দেয়া নতুন অংশ)
def manage_members():
    st.subheader("👥 মেম্বার ম্যানেজমেন্ট")
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users")
        members = cursor.fetchall()
        
    for member in members:
        m_username = member[0]
        col1, col_rem, col_del = st.columns([2, 2, 2])
        with col1:
            st.write(f"মেম্বার: **{m_username}**")
        with col_rem:
            rem_message = st.text_input(f"রিমাইন্ডার", key=f"rem_input_{m_username}")
            if st.button("সেন্ড", key=f"send_rem_{m_username}"):
                if rem_message:
                    with get_db_connection() as conn:
                        conn.execute("INSERT INTO notifications (username, message) VALUES (?, ?)", (m_username, rem_message))
                        conn.commit()
                    st.success(f"{m_username}-এর কাছে রিমাইন্ডার পাঠানো হয়েছে!")
        with col_del:
            if st.button(f"🗑️ রিমুভ", key=f"del_{m_username}"):
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM users WHERE username = ?", (m_username,))
                    cursor.execute("DELETE FROM sessions WHERE username = ?", (m_username,))
                    cursor.execute("DELETE FROM notifications WHERE username = ?", (m_username,))
                    conn.commit()
                st.success(f"{m_username} রিমুভ করা হয়েছে!")
                st.rerun()

# মেইন অ্যাপ লজিক
def main():
    check_persistent_login()
    
    if "logged_in" not in st.session_state:
        st.title("লগইন করুন")
        username = st.text_input("ইউজারনেম")
        password = st.text_input("পাসওয়ার্ড", type="password")
        if st.button("লগইন"):
            token = str(uuid.uuid4())
            st.query_params["session_token"] = token
            with get_db_connection() as conn:
                conn.execute("INSERT OR REPLACE INTO sessions (username, token) VALUES (?, ?)", (username, token))
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()
    else:
        st.title(f"স্বাগতম, {st.session_state.username}!")
        if st.button("লগআউট"):
            st.query_params.clear()
            st.session_state.clear()
            st.rerun()
            
        tab1, tab2 = st.tabs(["📺 ভিডিওসমূহ", "⚙️ ম্যানেজমেন্ট"])
        with tab1:
            display_videos()
        with tab2:
            manage_members()

if __name__ == "__main__":
    main()
