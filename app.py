import streamlit as st
import pandas as pd
import datetime
import time

# 1. முதலில் Page Config
st.set_page_config(page_title="ஜோதிடம் - Vedic Astrology", layout="wide")

# 2. Utils மாட்யூல்களை இறக்குமதி செய்தல்
# உங்கள் 'utils' ஃபோல்டரில் இந்த பங்க்ஷன்கள் சரியாக இருக்க வேண்டும்
try:
    from utils.vedic import calculate_chart
    from utils.predictions import get_predictions
    from utils.compatibility import check_compatibility
    from utils.database import save_profile, get_all_profiles
except ImportError as e:
    st.error(f"கோப்புகள் கிடைக்கவில்லை (Missing Utils): {e}")
    st.stop()

# --- CSS ஸ்டைலிங் (பழைய டிசைன்) ---
def load_css():
    st.markdown("""
    <style>
    .prediction-card { background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 15px; padding: 25px; color: white; }
    .metric-card { background: rgba(255,255,255,0.1); border-radius: 12px; padding: 20px; border: 1px solid rgba(255,255,255,0.2); }
    </style>
    """, unsafe_allow_html=True)

# --- மெனுக்கள் ---
def main():
    load_css()
    
    st.sidebar.title("🌟 ஜோதிடம்")
    menu = st.sidebar.radio("மெனு", ["முகப்பு", "புதிய ஜாதகம்", "கணிப்புகள்", "திருமண பொருத்தம்", "தசா வரிசை"])
    
    if menu == "முகப்பு":
        st.title("நல்வரவு!")
        st.write("உங்கள் ஜாதக விவரங்களை அறிய 'புதிய ஜாதகம்' செல்லவும்.")
        
    elif menu == "புதிய ஜாதகம்":
        st.subheader("புதிய ஜாதகம்")
        with st.form("profile_form"):
            name = st.text_input("பெயர்")
            dob = st.date_input("பிறந்த தேதி")
            tob = st.time_input("பிறந்த நேரம்")
            submit = st.form_submit_button("கணி")
            
        if submit:
            # utils.vedic-ல் உள்ள function-ஐ அழைத்தல்
            chart = calculate_chart(name, dob, tob)
            st.session_state['current_chart'] = chart
            # டேட்டாபேஸில் சேமித்தல்
            save_profile(chart)
            st.success("ஜாதகம் சேமிக்கப்பட்டது!")
            st.write(chart)
            
    elif menu == "கணிப்புகள்":
        if 'current_chart' in st.session_state:
            st.subheader("ஜாதக கணிப்புகள்")
            # utils.predictions-ஐ அழைத்தல்
            res = get_predictions(st.session_state['current_chart'])
            st.markdown(f'<div class="prediction-card">{res}</div>', unsafe_allow_html=True)
        else:
            st.warning("முதலில் ஜாதகம் கணிக்கவும்.")
            
    elif menu == "திருமண பொருத்தம்":
        st.subheader("திருமண பொருத்தம்")
        # utils.compatibility-ஐ அழைத்தல்
        check_compatibility()
        
    elif menu == "தசா வரிசை":
        st.subheader("தசா வரிசை")
        # இங்கே தசா கால்குலேஷன் லாஜிக் சேர்க்கவும்

if __name__ == "__main__":
    main()
