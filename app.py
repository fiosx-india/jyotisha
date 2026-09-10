"""
🔥 ஜோதிட பயன்பாடு - Vedic Astrology Prediction App
ஸ்ட்ரீம்லிட் (Streamlit) அடிப்படையிலான முழுமையான ஜோதிட கணிப்பு செயலி
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, time
from PIL import Image
import io
import base64
import plotly.graph_objects as go
import plotly.express as px

from utils.constants import (
    RASI_TAMIL, RASI_ENGLISH, NAKSHATRAS, PLANETS_TAMIL,
    PLANET_SIGNFICANCE, PORUTHAM_LIST
)
from utils.vedic import BirthChart
from utils.predictions import PredictionEngine
from utils.compatibility import CompatibilityEngine
from utils.database import ProfileDatabase

import streamlit as st
# ---------------------------------------------------------------
# பக்க கட்டமைப்பு (Page Config)
# ---------------------------------------------------------------
st.set_page_config(
    page_title="🔥 ஜோதிடம் - Vedic Astrology",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------------
# CSS ஸ்டைலிங்
# ---------------------------------------------------------------
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Tamil:wght@300;400;500;700&display=swap');
    
    * {
        font-family: 'Noto Sans Tamil', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .prediction-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 5px solid #667eea;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .dasha-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    
    .planet-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        margin: 0.5rem 0;
        border: 1px solid #e0e0e0;
    }
    
    .porutham-good {
        background: linear-gradient(135deg, #a8e063 0%, #56ab2f 100%);
        color: white;
        padding: 0.5rem;
        border-radius: 8px;
        text-align: center;
    }
    
    .porutham-bad {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        color: white;
        padding: 0.5rem;
        border-radius: 8px;
        text-align: center;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        text-align: center;
        transition: transform 0.3s;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .sidebar-header {
        font-size: 1.2rem;
        font-weight: 700;
        color: #764ba2;
        margin-bottom: 1rem;
    }
    
    .tab-custom {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
    }
    
    .footer {
        text-align: center;
        padding: 2rem;
        color: #666;
        font-size: 0.9rem;
    }

    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 50px;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
    }
    
    .highlight-text {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------
# தரவுத்தளம் ஆரம்பித்தல்
# ---------------------------------------------------------------
@st.cache_resource
def init_database():
    return ProfileDatabase()

# ---------------------------------------------------------------
# பக்க தலைப்பு
# ---------------------------------------------------------------
def show_header():
    st.markdown("""
    <div class="main-header">
        <h1>🌟 ஜோதிடம் - முழுமையான கணிப்பு செயலி</h1>
        <p style="font-size: 1.1rem; opacity: 0.9;">
            வேத ஜோதிடம் | கைரேகை | திருமண பொருத்தம் | தசா கணிப்புகள்
        </p>
        <p style="font-size: 0.9rem; opacity: 0.8;">
            எத்தனை வருடங்கள் வேண்டுமானாலும் - தெளிவான கணிப்புகள்!
        </p>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------
# பக்க வழிசெலுத்தல் (Sidebar Navigation)
# ---------------------------------------------------------------
def show_sidebar():
    with st.sidebar:
        st.markdown('<div class="sidebar-header">🧭 மெனு</div>', unsafe_allow_html=True)
        
        menu = st.radio(
            "",
            ["🏠 முகப்பு", "👤 புதிய ஜாதகம்", "🔮 கணிப்புகள்", 
             "💑 திருமண பொருத்தம்", "✋ கைரேகை", "📋 சுயவிவரங்கள்"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("### 📅 இன்றைய தேதி")
        st.info(f"{datetime.now().strftime('%d-%m-%Y')}")
        
        st.markdown("---")
        st.markdown("### ⚡ விரைவு தகவல்")
        
        db = init_database()
        profile_count = db.get_profile_count()
        st.metric("மொத்த சுயவிவரங்கள்", profile_count)
        
        st.markdown("---")
        st.markdown("""
        <div style="font-size: 0.8rem; color: #666;">
        <b>⚙️ பதிப்பு:</b> 1.0.0<br>
        <b>🛠️ உருவாக்கியவர்:</b> ஜோதிட செயலி<br>
        <b>📧</b> Streamlit அடிப்படை
        </div>
        """, unsafe_allow_html=True)
        
        return menu

# ---------------------------------------------------------------
# புதிய சுயவிவரம் உருவாக்கம்
# ---------------------------------------------------------------
def create_profile_form():
    st.markdown("## 👤 புதிய சுயவிவரம் உருவாக்குக")
    st.markdown("உங்கள் பிறந்த தேதி, நேரம் மற்றும் இடத்தை உள்ளிடவும்.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("**பெயர்**", placeholder="உங்கள் பெயரை உள்ளிடவும்")
        birth_date = st.date_input(
            "**பிறந்த தேதி**",
            value=date(1990, 1, 1),
            min_value=date(1900, 1, 1),
            max_value=date.today()
        )
        birth_time = st.time_input(
            "**பிறந்த நேரம்**",
            value=time(6, 0)
        )
    
    with col2:
        birth_place = st.text_input("**பிறந்த இடம்**", placeholder="சென்னை, தமிழ்நாடு")
        latitude = st.number_input("**அட்சரேகை (Latitude)**", value=13.0, 
                                    format="%.4f", help="சென்னை: 13.0, மதுரை: 9.9")
        longitude = st.number_input("**தீர்க்க ரேகை (Longitude)**", value=80.0, 
                                     format="%.4f", help="சென்னை: 80.0, மதுரை: 78.1")
    
    if st.button("🔮 ஜாதகம் கணிக்கவும்", use_container_width=True):
        if not name:
            st.error("தயவுசெய்து உங்கள் பெயரை உள்ளிடவும்.")
            return None
        
        birth_datetime = datetime.combine(birth_date, birth_time)
        
        with st.spinner("🔥 ஜாதகம் கணிக்கப்படுகிறது..."):
            chart = BirthChart(name, birth_datetime, birth_place, latitude, longitude)
            
            # Save to database
            db = init_database()
            profile_id = f"profile_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            profile_data = {
                "name": name,
                "birth_date": birth_datetime.isoformat(),
                "birth_place": birth_place,
                "latitude": latitude,
                "longitude": longitude,
                "age": chart.age,
                "moon_rasi": chart.rasi_positions.get("Moon", 0),
                "moon_nakshatra": chart.moon_nakshatra_name,
                "lagna": chart.lagna_rasi,
                "created_at": datetime.now().isoformat()
            }
            db.add_profile(profile_id, profile_data)
            
            st.success(f"✅ {name} அவர்களின் ஜாதகம் வெற்றிகரமாக கணக்கிடப்பட்டது!")
            
            return chart, profile_id
        
    return None, None

# ---------------------------------------------------------------
# ஜாதக விவரங்கள் காண்பித்தல்
# ---------------------------------------------------------------
def display_chart(chart: BirthChart):
    """ஜாதக விவரங்களை காண்பிக்கும்"""
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("🎂 வயது", f"{chart.age:.1f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("🌙 சந்திர ராசி", 
                  RASI_TAMIL.get(chart.rasi_positions.get("Moon", 0), ""))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("🔆 லக்னம்", 
                  RASI_TAMIL.get(chart.lagna_rasi, ""))
        st.markdown('</div>', unsafe_allow_html=True)
    
    # கிரக நிலைகள்
    st.markdown("## 🪐 கிரக நிலைகள்")
    
    planets_data = chart.get_planet_details()
    cols = st.columns(3)
    
    for i, p in enumerate(planets_data):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="planet-card">
                <h4>{p['planet_tamil']} ({p['planet_english']})</h4>
                <p><b>ராசி:</b> {p['rasi_tamil']}</p>
                <p><b>தீர்க்க ரேகை:</b> {p['sidereal_longitude']}°</p>
            </div>
            """, unsafe_allow_html=True)
    
    # நட்சத்திர தகவல்
    st.markdown("## ⭐ நட்சத்திர தகவல்")
    
    nak = chart.get_nakshatra_details()
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="prediction-card">
            <h4>🌙 பிறந்த நட்சத்திரம்</h4>
            <p><b>நட்சத்திரம்:</b> {nak['moon']['nakshatra_tamil']} ({nak['moon']['nakshatra_english']})</p>
            <p><b>பாதம்:</b> {nak['moon']['pada']}</p>
            <p><b>நட்சத்திர நாதர்:</b> {nak['moon']['lord']}</p>
            <p><b>அதிதெய்வம்:</b> {nak['moon']['deity']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="prediction-card">
            <h4>☀️ சூரிய நட்சத்திரம்</h4>
            <p><b>நட்சத்திரம்:</b> {nak['sun']['nakshatra_tamil']} ({nak['sun']['nakshatra_english']})</p>
            <p><b>பாதம்:</b> {nak['sun']['pada']}</p>
            <p><b>நட்சத்திர நாதர்:</b> {nak['sun']['lord']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # தசா தகவல்
    st.markdown("## 📅 தசா பருவங்கள்")
    
    dasha_df = pd.DataFrame(chart.dasha_sequence[:15])  # Show first 15
    dasha_df['lord'] = dasha_df['lord'].map(lambda x: PLANETS_TAMIL.get(x, x))
    dasha_df = dasha_df[['lord', 'start_age', 'end_age', 'total_years']]
    dasha_df.columns = ['கிரகம்', 'தொடக்கம் (வயது)', 'முடிவு (வயது)', 'கால அளவு (ஆண்டுகள்)']
    
    st.dataframe(dasha_df, use_container_width=True, hide_index=True)
    
    # Current dasha highlight
    if chart.current_dasha:
        st.markdown(f"""
        <div class="dasha-card">
            <h4>⚡ தற்போதைய தசா</h4>
            <p><b>கிரகம்:</b> {PLANETS_TAMIL.get(chart.current_dasha['lord'], chart.current_dasha['lord'])}</p>
            <p><b>காலம்:</b> வயது {chart.current_dasha['start_age']} முதல் {chart.current_dasha['end_age']} வரை</p>
            <p><b>எஞ்சியுள்ளது:</b> {round(chart.current_dasha['end_age'] - chart.age, 1)} ஆண்டுகள்</p>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------------
# கணிப்புகள் பக்கம்
# ---------------------------------------------------------------
def predictions_page(chart: BirthChart):
    """கணிப்புகளை காண்பிக்கும் பக்கம்"""
    
    st.markdown("## 🔮 முழுமையான கணிப்புகள்")
    
    engine = PredictionEngine(chart)
    
    # Tab structure
    tab1, tab2, tab3 = st.tabs(["📊 தற்போதைய கணிப்பு", "📅 எதிர்கால கணிப்புகள்", "📋 முழு அறிக்கை"])
    
    with tab1:
        st.markdown("### 📊 தற்போதைய நிலை கணிப்புகள்")
        
        predictions = engine.generate_current_predictions()
        
        # Overall prediction
        st.markdown(f"""
        <div class="prediction-card">
            {predictions['overall']['prediction']}
        </div>
        """, unsafe_allow_html=True)
        
        # Summary points
        st.markdown("### 📌 முக்கிய புள்ளிகள்")
        for point in predictions['overall']['summary_points']:
            st.markdown(f"- {point}")
        
        # Dasha details
        st.markdown("### 🪐 தசா விவரங்கள்")
        dasha = predictions['dasha']
        if dasha.get('main_dasha'):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                **முதன்மை தசா:** {dasha['main_dasha']['lord_tamil']}
                - மீதம்: {dasha['main_dasha']['remaining']} ஆண்டுகள்
                - காலம்: வயது {dasha['main_dasha']['start_age']} - {dasha['main_dasha']['end_age']}
                """)
            with col2:
                if dasha.get('antardasha'):
                    st.markdown(f"""
                    **பூர்த்தி தசா:** {dasha['antardasha']['lord_tamil']}
                    """)
        
        # Age prediction
        st.markdown("### 🎂 வயது கணிப்பு")
        st.info(predictions['age']['prediction'])
    
    with tab2:
        st.markdown("### 📅 எதிர்கால கணிப்புகள்")
        st.markdown("எத்தனை வருடங்கள் முன்னால் கணிக்க வேண்டும்?")
        
        years = st.slider("ஆண்டுகள்", 1, 50, 10, 
                          help="எத்தனை வருடங்கள் முன்னால் கணிப்பது என்பதை தேர்ந்தெடுக்கவும்")
        
        if st.button(f"🔮 {years} ஆண்டுகளுக்கான கணிப்பு", use_container_width=True):
            with st.spinner(f"🔥 {years} ஆண்டுகளுக்கான கணிப்புகள் கணக்கிடப்படுகின்றன..."):
                future_preds = engine.generate_future_predictions(years)
                
                # Summary
                st.markdown("### 📜 முழுமையான கணிப்பு")
                st.markdown(f"""
                <div class="prediction-card">
                    {future_preds['summary']}
                </div>
                """, unsafe_allow_html=True)
                
                # Year-by-year table
                st.markdown("### 📊 ஆண்டு வாரிய கணிப்புகள்")
                
                yearly_data = []
                for key, pred in future_preds['yearly'].items():
                    yearly_data.append({
                        "ஆண்டு": pred.get('year', ''),
                        "வயது": pred.get('age', ''),
                        "தசா": pred.get('dasha_tamil', ''),
                        "கணிப்பு": pred.get('prediction', '')[:80] + "...",
                        "எச்சரிக்கை": pred.get('caution', '')[:80] + "..."
                    })
                
                if yearly_data:
                    df = pd.DataFrame(yearly_data)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                
                # Future dasha periods
                if future_preds.get('dasha_periods'):
                    st.markdown("### 📅 வரும் தசா காலங்கள்")
                    for d in future_preds['dasha_periods']:
                        st.markdown(f"""
                        <div class="dasha-card">
                            <b>{d['lord_tamil']}</b> - வயது {d['start_age']} முதல் {d['end_age']} வரை
                            <br>✨ {d['prediction'][:100]}
                        </div>
                        """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("### 📋 முழுமையான ஜோதிட அறிக்கை")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 👤 நபர் விவரங்கள்")
            st.markdown(f"**பெயர்:** {chart.name}")
            st.markdown(f"**பிறந்த தேதி:** {chart.birth_date.strftime('%Y-%m-%d %H:%M')}")
            st.markdown(f"**வயது:** {chart.age:.1f}")
            st.markdown(f"**லக்னம்:** {RASI_TAMIL.get(chart.lagna_rasi, '')}")
        
        with col2:
            st.markdown("#### 🌌 வானியல் தகவல்கள்")
            st.markdown(f"**சூரிய ராசி:** {RASI_TAMIL.get(chart.rasi_positions.get('Sun', 0), '')}")
            st.markdown(f"**சந்திர ராசி:** {RASI_TAMIL.get(chart.rasi_positions.get('Moon', 0), '')}")
            st.markdown(f"**சந்திர நட்சத்திரம்:** {chart.moon_nakshatra_name}")
            st.markdown(f"**அயனாம்சம்:** {chart.ayanamsa:.3f}°")
        
        # Planet table
        st.markdown("#### 🪐 கிரக விவரங்கள்")
        planets_data = chart.get_planet_details()
        pdf = pd.DataFrame(planets_data)
        pdf = pdf[['planet_tamil', 'planet_english', 'rasi_tamil', 'sidereal_longitude']]
        pdf.columns = ['கிரகம் (தமிழ்)', 'கிரகம் (ஆங்கிலம்)', 'ராசி', 'தீர்க்க ரேகை']
        st.dataframe(pdf, use_container_width=True, hide_index=True)

# ---------------------------------------------------------------
# திருமண பொருத்தம் பக்கம்
# ---------------------------------------------------------------
def compatibility_page():
    st.markdown("## 💑 திருமண பொருத்தம்")
    st.markdown("இரண்டு நபர்களின் ஜாதகங்களை ஒப்பிட்டு பொருத்தம் பார்க்கவும்.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👤 முதல் நபர்")
        name1 = st.text_input("**பெயர்**", key="name1", placeholder="மணம���ன்")
        date1 = st.date_input("**பிறந்த தேதி**", key="date1")
        time1 = st.time_input("**பிறந்த நேரம்**", key="time1", value=time(6, 0))
        place1 = st.text_input("**இடம்**", key="place1", placeholder="சென்னை")
        lat1 = st.number_input("**Latitude**", key="lat1", value=13.0)
        lon1 = st.number_input("**Longitude**", key="lon1", value=80.0)
    
    with col2:
        st.markdown("### 👤 இரண்டாவது நபர்")
        name2 = st.text_input("**பெயர்**", key="name2", placeholder="மணமகள்")
        date2 = st.date_input("**பிறந்த தேதி**", key="date2")
        time2 = st.time_input("**பிறந்த நேரம்**", key="time2", value=time(6, 0))
        place2 = st.text_input("**இடம்**", key="place2", placeholder="சென்னை")
        lat2 = st.number_input("**Latitude**", key="lat2", value=13.0)
        lon2 = st.number_input("**Longitude**", key="lon2", value=80.0)
    
    if st.button("💑 பொருத்தம் கணிக்கவும்", use_container_width=True):
        if not name1 or not name2:
            st.error("தயவுசெய்து இரண்டு நபர்களின் பெயர்களையும் உள்ளிடவும்.")
            return
        
        with st.spinner("🔥 பொருத்தம் கணக்கிடப்படுகிறது..."):
            dt1 = datetime.combine(date1, time1)
            dt2 = datetime.combine(date2, time2)
            
            chart1 = BirthChart(name1, dt1, place1, lat1, lon1)
            chart2 = BirthChart(name2, dt2, place2, lat2, lon2)
            
            compat = CompatibilityEngine(chart1, chart2, name1, name2)
            report = compat.generate_compatibility_report()
            
            # Display results
            st.markdown("---")
            st.markdown("## 📊 பொருத்த முடிவுகள்")
            
            # Overall score
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("📊 மொத்த மதிப்பெண்", 
                         f"{report['porutham']['total_score']}/{report['porutham']['max_score']}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("📈 சதவீதம்", f"{report['porutham']['overall_percentage']}%")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("✅ பொருத்தங்கள்", 
                         f"{report['porutham']['total_poruthams']}/{report['porutham']['total_poruthams_max']}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Verdict
            verdict = report['porutham']['verdict']
            st.markdown(f"""
            <div style="text-align: center; padding: 2rem; 
                 background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                 border-radius: 15px; color: white; margin: 1rem 0;">
                <h2>{verdict['emoji']} {verdict['text']}</h2>
            </div>
            """, unsafe_allow_html=True)
            
            # Porutham details
            st.markdown("###")
