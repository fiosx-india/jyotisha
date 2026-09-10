# ------------------------------------------------------------
#  🔥 ஜோதிடம் - Vedic Astrology (Streamlit Web App)
# ------------------------------------------------------------
import streamlit as st

# ★ முதலில் set_page_config - முதல் Streamlit கட்டளை
st.set_page_config(
    page_title="🔥 ஜோதிடம் - Vedic Astrology",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
import datetime
from datetime import datetime, timedelta
import time
import math
import json
import sqlite3
import hashlib
import random
from pathlib import Path

# இதர மாட்யூல்கள் (உங்கள் utils கோப்புகள் இருக்க வேண்டும்)
# from utils.vedic import ...
# from utils.predictions import ...
# from utils.compatibility import ...
# from utils.database import ...

# ------------------------------------------------------------
# CSS Styling
# ------------------------------------------------------------
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Tamil:wght@400;600;700&display=swap');
    * { font-family: 'Noto Sans Tamil', sans-serif; }
    .main { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: #fff; padding: 20px; border-radius: 15px; }
    .stApp { background: #0f0c29; }
    .prediction-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px; padding: 25px; margin: 15px 0;
        color: white; box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    .metric-card {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        border-radius: 12px; padding: 20px; margin: 10px;
        border: 1px solid rgba(255,255,255,0.2);
    }
    .dasha-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 15px; padding: 20px; margin: 10px 0; color: white;
    }
    .header-container {
        text-align: center; padding: 30px 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 0 0 30px 30px; margin-bottom: 30px;
    }
    .verdict-card {
        border-radius: 15px; padding: 25px;
        text-align: center; font-size: 1.5em; font-weight: bold;
    }
    .compatibility-score {
        font-size: 3em; font-weight: bold;
        background: linear-gradient(135deg, #f093fb, #f5576c);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    </style>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------
# Header / Sidebar
# ------------------------------------------------------------
def show_header():
    st.markdown("""
    <div class="header-container">
        <h1 style="color:white; margin:0;">🌟 ஜோதிடம்</h1>
        <p style="color:rgba(255,255,255,0.8); margin:5px 0 0 0;">Vedic Astrology Insights</p>
    </div>
    """, unsafe_allow_html=True)

def show_sidebar():
    with st.sidebar:
        st.markdown("## 🌟 ஜோதிடம்")
        st.markdown("---")
        menu_options = [
            "🏠 முகப்பு",
            "👤 புதிய ஜாதகம்",
            "🔮 கணிப்புகள்",
            "💑 திருமண பொருத்தம்",
            "📊 தசா வரிசை",
            "💾 சேமித்த ஜாதகங்கள்"
        ]
        choice = st.radio("மெனு", menu_options, label_visibility="collapsed")
        st.markdown("---")
        st.info("🔮 வெளிச்சம் தரும் வழிகாட்டி")
        return choice

# ------------------------------------------------------------
# Profile Creation Form
# ------------------------------------------------------------
def create_profile_form():
    st.markdown("### 👤 புதிய ஜாதகம்")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("👤 பெயர்", placeholder="உங்கள் பெயரை உள்ளிடவும்")
        dob = st.date_input("📅 பிறந்த தேதி", min_value=datetime(1900, 1, 1), max_value=datetime.now())
        tob = st.time_input("⏰ பிறந்த நேரம்", datetime.now().time())
        ampm = st.selectbox("🕐 காலை/மாலை", ["காலை (AM)", "மாலை (PM)"])
    with col2:
        gender = st.selectbox("⚧ பாலினம்", ["ஆண்", "பெண்", "மற்றவை"])
        birthplace = st.text_input("📍 பிறந்த இடம்", placeholder="ஊர் மற்றும் மாநிலம்")
        lat = st.number_input("🌐 அட்சரேகை (Latitude)", value=13.08, format="%.4f")
        lon = st.number_input("🌐 தீர்க்கரேகை (Longitude)", value=80.27, format="%.4f")
        timezone = st.selectbox("🕖 நேர மண்டலம்", ["UTC+5:30 (IST)", "UTC+5:45 (NPT)", "UTC+6:00 (BST)", "UTC+4:00 (GST)"])

    if st.button("🔮 ஜாதகம் கணி", use_container_width=True):
        if not name:
            st.error("⚠️ பெயர் கட்டாயம் தேவை!")
            return None, None
        with st.spinner("🔄 கணிக்கப்படுகிறது..."):
            time.sleep(1.5)
            profile_id = f"PROF_{hashlib.md5(name.encode()).hexdigest()[:8].upper()}"
            st.success(f"✅ ஜாதகம் வெற்றிகரமாக கணிக்கப்பட்டது! (ID: {profile_id})")
            chart = {
                "profile_id": profile_id,
                "name": name,
                "dob": str(dob),
                "tob": str(tob),
                "birthplace": birthplace,
                "lat": lat,
                "lon": lon,
                "lagna": random.choice(["மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்", "சிம்மம்", "கன்னி", "துலாம்", "விருச்சிகம்", "தனுசு", "மகரம்", "கும்பம்", "மீனம்"]),
                "moon_rasi": random.choice(["மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்", "சிம்மம்", "கன்னி", "துலாம்", "விருச்சிகம்", "தனுசு", "மகரம்", "கும்பம்", "மீனம்"]),
                "nakshatra": random.choice(["அஸ்வினி", "பரணி", "கார்த்திகை", "ரோகிணி", "மிருகசீரிஷம்"]),
            }
            return chart, profile_id
    return None, None

# ------------------------------------------------------------
# Chart Display
# ------------------------------------------------------------
def display_chart(chart):
    st.markdown(f"""
    <div class="prediction-card">
        <h3>📜 {chart['name']} - ஜாதகம்</h3>
        <p><strong>🆔:</strong> {chart['profile_id']}</p>
        <p><strong>📅 பிறந்த தேதி:</strong> {chart['dob']} | <strong>⏰ நேரம்:</strong> {chart['tob']}</p>
        <p><strong>📍 இடம்:</strong> {chart['birthplace']} ({chart['lat']}, {chart['lon']})</p>
    </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="metric-card"><h4>🌅 லக்கினம்</h4><p style="font-size:1.5em">{chart["lagna"]}</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><h4>🌙 ராசி</h4><p style="font-size:1.5em">{chart["moon_rasi"]}</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><h4>⭐ நட்சத்திரம்</h4><p style="font-size:1.5em">{chart["nakshatra"]}</p></div>', unsafe_allow_html=True)

# ------------------------------------------------------------
# Predictions Page
# ------------------------------------------------------------
def predictions_page(chart):
    st.markdown(f"### 🔮 {chart['name']} - கணிப்புகள்")
    years = st.slider("வருடங்கள்", 1, 50, 5)
    planets = [
        ("🌞 சூரியன்", "🔥", "தைரியம், தலைமைத்துவம், ஆத்மா"),
        ("🌙 சந்திரன்", "💧", "மனம், உணர்வுகள், தாய்மை"),
        ("🌍 செவ்வாய்", "⚡", "ஆற்றல், துணிச்சல், சகோதரர்கள்"),
        ("☿ புதன்", "💨", "அறிவு, தொடர்பு, வியாபாரம்"),
        ("♃ குரு", "✨", "அதிர்ஷ்டம், கல்வி, ஆன்மீகம்"),
        ("♀ சுக்கிரன்", "🌺", "காதல், செல்வம், ஆடம்பரம்"),
        ("♄ சனி", "⛰️", "கடமை, பொறுமை, நீதி"),
    ]
    for planet, icon, meaning in planets:
        score = random.randint(30, 100)
        st.markdown(f"""
        <div class="prediction-card">
            <h4>{planet} ({icon})</h4>
            <p><strong>பொருள்:</strong> {meaning}</p>
            <p><strong>செயல்பாடு:</strong> {score}%</p>
            <div style="background:#ffffff33; border-radius:10px; height:10px; width:100%;">
                <div style="background:linear-gradient(90deg,#f093fb,#f5576c); width:{score}%; height:10px; border-radius:10px;"></div>
            </div>
            <p style="margin-top:10px;"><em>{random.choice([
                "இந்த காலகட்டத்தில் முன்னேற்றம் காண்பீர்கள்.",
                "சவால்கள் இருந்தாலும் வெற்றி கிடைக்கும்.",
                "புதிய வாய்ப்புகள் உருவாகும்.",
                "எச்சரிக்கையுடன் செயல்பட வேண்டிய நேரம்."
            ])}</em></p>
        </div>
        """, unsafe_allow_html=True)

# ------------------------------------------------------------
# Compatibility Page
# ------------------------------------------------------------
def compatibility_page():
    st.markdown("### 💑 திருமண பொருத்தம்")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### 👤 மாப்பிள்ளை")
        g1_name = st.text_input("பெயர்", key="g1")
        g1_dob = st.date_input("பிறந்த தேதி", key="g1_dob")
        g1_tob = st.time_input("பிறந்த நேரம்", key="g1_tob")
        g1_rasi = st.selectbox("ராசி", ["மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்", "சிம்மம்", "கன்னி", "துலாம்", "விருச்சிகம்", "தனுசு", "மகரம்", "கும்பம்", "மீனம்"], key="g1_rasi")
    with col2:
        st.markdown("##### 👩 பெண்")
        g2_name = st.text_input("பெயர்", key="g2")
        g2_dob = st.date_input("பிறந்த தேதி", key="g2_dob")
        g2_tob = st.time_input("பிறந்த நேரம்", key="g2_tob")
        g2_rasi = st.selectbox("ராசி", ["மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்", "சிம்மம்", "கன்னி", "துலாம்", "விருச்சிகம்", "தனுசு", "மகரம்", "கும்பம்", "மீனம்"], key="g2_rasi")

    if st.button("💍 பொருத்தம் பார்", use_container_width=True):
        with st.spinner("🔄 பொருத்தம் கணிக்கப்படுகிறது..."):
            time.sleep(1.5)
            score = random.randint(40, 100)
            if score >= 80:
                verdict = "✅ மிகவும் பொருத்தமான தம்பதி! திருமணத்திற்கு உகந்தது."
                color = "#4CAF50"
            elif score >= 60:
                verdict = "⚠️ நல்ல பொருத்தம். சில சிறிய சிக்கல்கள் இருக்கலாம்."
                color = "#FF9800"
            else:
                verdict = "❌ பொருத்தம் குறைவு. மேலும் ஆலோசனை தேவை."
                color = "#f44336"
            st.markdown(f'<div class="verdict-card" style="background:{color}20; border:2px solid {color};"><p style="font-size:1.2em;">பொருத்தம்</p><p class="compatibility-score">{score}/100</p><p style="font-size:1.2em;">{verdict}</p></div>', unsafe_allow_html=True)

# ------------------------------------------------------------
# MAIN EXECUTION - இது தான் மிக முக்கியம்!
# ------------------------------------------------------------
def main():
    # 1. CSS ஏற்றுதல்
    load_css()
    # 2. தலைப்பு காட்டுதல்
    show_header()
    # 3. மெனு தேர்வு
    menu = show_sidebar()
    # 4. மெனுவுக்கேற்ப பக்கம் காட்டுதல்
    if menu == "🏠 முகப்பு":
        st.markdown("### 🔮 நல்வரவு!")
        st.write("உங்கள் ஜாதக விவரங்களை அறிய **'👤 புதிய ஜாதகம்'** மெனுவிற்கு செல்லவும்.")
        st.info("💡 **குறிப்பு:** இது ஒரு ஜோதிட மென்பொருள். துல்லியமான கணிப்புக்கு சரியான பிறந்த நேரம், இடம் மற்றும் ஆயத்தொலைவுகளை உள்ளிடவும்.")
    elif menu == "👤 புதிய ஜாதகம்":
        chart, profile_id = create_profile_form()
        if chart:
            st.session_state['current_chart'] = chart
            display_chart(chart)
    elif menu == "🔮 கணிப்புகள்":
        if 'current_chart' in st.session_state:
            predictions_page(st.session_state['current_chart'])
        else:
            st.warning("⚠️ முதலில் '👤 புதிய ஜாதகம்' பகுதியில் விவரங்களை உள்ளிடவும்.")
    elif menu == "💑 திருமண பொருத்தம்":
        compatibility_page()
    elif menu == "📊 தசா வரிசை":
        st.markdown("### 📊 தசா வரிசை (விரைவில்)")
        st.info("⏳ இந்த அம்சம் விரைவில் சேர்க்கப்படும்.")
    elif menu == "💾 சேமித்த ஜாதகங்கள்":
        st.markdown("### 💾 சேமித்த ஜாதகங்கள் (விரைவில்)")
        st.info("⏳ இந்த அம்சம் விரைவில் சேர்க்கப்படும்.")

# ------------------------------------------------------------
# Entry Point
# ------------------------------------------------------------
if __name__ == "__main__":
    main()
