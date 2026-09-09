"""
வானியல் கணக்கீடுகள்
Astronomical calculations for Jyotisha
"""
import math
from datetime import datetime, timedelta
from typing import Tuple, Dict, Optional

# ---------------------------------------------------------------
# 1. ஜூலியன் நாள் கணக்கீடு (Julian Day Number)
# ---------------------------------------------------------------
def julian_day_number(year: int, month: int, day: float) -> float:
    """
    கிரிகோரியன் தேதியிலிருந்து ஜூலியன் நாள் எண்ணை கணக்கிடுகிறது.
    """
    if month <= 2:
        year -= 1
        month += 12
    
    A = math.floor(year / 100)
    B = 2 - A + math.floor(A / 4)
    
    jdn = math.floor(365.25 * (year + 4716)) + math.floor(30.6001 * (month + 1)) + day + B - 1524.5
    return jdn

# ---------------------------------------------------------------
# 2. சூரியனின் உண்மையான தீர்க்க ரேகை (Sun's True Longitude)
# ---------------------------------------------------------------
def sun_longitude(jd: float) -> float:
    """
    சூரியனின் தீர்க்க ரேகையை கணக்கிடுகிறது (எளிமைப்படுத்தப்பட்ட வானியல் வாய்பாடு).
    Returns degrees (0-360).
    """
    T = (jd - 2451545.0) / 36525.0  # ஜூலியன் நூற்றாண்டுகள் J2000.0 இலிருந்து
    
    # Mean anomaly of Sun (degrees)
    M = 357.52911 + 35999.05029 * T - 0.0001537 * T * T
    M = M % 360
    
    # Mean longitude of Sun
    L0 = 280.46646 + 36000.76983 * T + 0.0003032 * T * T
    L0 = L0 % 360
    
    # Center equation
    C = (1.914602 - 0.004817 * T - 0.000014 * T * T) * math.sin(math.radians(M))
    C += (0.019993 - 0.000101 * T) * math.sin(math.radians(2 * M))
    C += 0.000289 * math.sin(math.radians(3 * M))
    
    # True longitude
    true_lon = L0 + C
    true_lon = true_lon % 360
    
    # Apparent longitude (with nutation correction)
    # Omega = 125.04 - 1934.136 * T
    # true_lon += -0.00569 - 0.00478 * math.sin(math.radians(Omega))
    
    return true_lon

# ---------------------------------------------------------------
# 3. சந்திரனின் தீர்க்க ரேகை (Moon's Longitude)
# ---------------------------------------------------------------
def moon_longitude(jd: float) -> float:
    """
    சந்திரனின் தீர்க்க ரேகையை கணக்கிடுகிறது (எளிமைப்படுத்தப்பட்ட வாய்பாடு).
    Returns degrees (0-360).
    """
    T = (jd - 2451545.0) / 36525.0
    
    # Moon's mean longitude
    L_prime = 218.3165 + 481267.8813 * T
    L_prime = L_prime % 360
    
    # Moon's mean anomaly
    M = 134.9629 + 477198.8676 * T
    M = M % 360
    
    # Sun's mean anomaly
    M_sun = 357.52911 + 35999.05029 * T
    M_sun = M_sun % 360
    
    # Moon's argument of latitude
    F = 93.2720 + 483202.0175 * T
    F = F % 360
    
    # Evection, variation, and annual equation
    evection = 1.2739 * math.sin(math.radians(2 * (L_prime - sun_longitude(jd)) - M))
    variation = 0.6583 * math.sin(math.radians(2 * (L_prime - sun_longitude(jd))))
    annual_eq = 0.1856 * math.sin(math.radians(M_sun))
    
    # Corrections
    M_corrected = M + evection - annual_eq - variation
    
    # Final longitude
    lon = L_prime + evection + variation + annual_eq
    lon = lon + 0.1098 * math.sin(math.radians(M_corrected))  # Additional correction
    
    lon = lon % 360
    return lon

# ---------------------------------------------------------------
# 4. நவகிரகங்களின் தோராய நிலைகள் (Approximate Planetary Positions)
# ---------------------------------------------------------------
def planetary_positions(jd: float) -> Dict[str, float]:
    """
    கிரகங்களின் தோராய நிலைகளை கணக்கிடுகிறது.
    இது எளிமைப்படுத்தப்பட்ட கணக்கீடு. துல்லியத்திற்கு Swiss Ephemeris பயன்படுத்தவும்.
    """
    T = (jd - 2451545.0) / 36525.0
    
    # Simplified mean longitudes for planets
    planets = {
        "Sun": sun_longitude(jd),
        "Moon": moon_longitude(jd),
        "Mercury": 252.2509 + 538101628.29 * T / 3600 + 0.0,  # Simplified
        "Venus": 181.9798 + 210664136.43 * T / 3600,
        "Mars": 355.4530 + 68905077.59 * T / 3600,
        "Jupiter": 34.3515 + 10925660.57 * T / 3600,
        "Saturn": 50.0774 + 4399609.86 * T / 3600,
        "Rahu": 0.0,  # Will be calculated below
        "Ketu": 0.0
    }
    
    # Normalize to 0-360
    for p in planets:
        planets[p] = planets[p] % 360
    
    # Rahu (North Node) - Mean node
    rahu_long = 125.044556 - 1934.136185 * T + 0.002076 * T * T
    rahu_long = rahu_long % 360
    planets["Rahu"] = rahu_long
    planets["Ketu"] = (rahu_long + 180) % 360
    
    return planets

# ---------------------------------------------------------------
# 5. அயனாம்சம் (Precession / Ayanamsa)
# ---------------------------------------------------------------
def calculate_ayanamsa(jd: float) -> float:
    """
    லஹிரி அயனாம்சத்தை கணக்கிடுகிறது.
    """
    # Simplified Lahiri ayanamsa calculation
    T = (jd - 2451545.0) / 36525.0
    # Base value at J2000 = 23.8478 degrees, precession rate ~0.01397 deg/year
    years_from_2000 = (jd - 2451545.0) / 365.25
    ayanamsa = 23.8478 + years_from_2000 * 0.01397
    return ayanamsa

# ---------------------------------------------------------------
# 6. சைடீரியல் தீர்க்க ரேகை (Sidereal Longitude)
# ---------------------------------------------------------------
def sidereal_longitude(tropical_longitude: float, ayanamsa: float) -> float:
    """
    Tropical longitude ஐ sidereal longitude ஆக மாற்றுகிறது.
    """
    sidereal = tropical_longitude - ayanamsa
    if sidereal < 0:
        sidereal += 360
    return sidereal

# ---------------------------------------------------------------
# 7. ராசி மற்றும் நட்சத்திர கணக்கீடு
# ---------------------------------------------------------------
def get_rasi(sidereal_lon: float) -> int:
    """சைடீரியல் தீர்க்க ரேகையிலிருந்து ராசி எண்ணை (1-12) கணக்கிடுகிறது."""
    return (int(sidereal_lon / 30) % 12) + 1

def get_nakshatra_and_pada(sidereal_lon: float) -> Tuple[int, int, str, int]:
    """
    சைடீரியல் தீர்க்க ரேகையிலிருந்து நட்சத்திரம் மற்றும் பாதத்தை கணக்கிடுகிறது.
    Returns: (nakshatra_number_1_to_27, pada_1_to_4, nakshatra_name, pada_number)
    """
    # Each nakshatra spans 13.3333 degrees
    from utils.constants import NAKSHATRAS
    
    nakshatra_index = int(sidereal_lon / 13.3333333)
    if nakshatra_index >= 27:
        nakshatra_index = 26
    
    pada = int((sidereal_lon - (nakshatra_index * 13.3333333)) / 3.3333333) + 1
    if pada > 4:
        pada = 4
    
    nakshatra_num = nakshatra_index + 1
    nakshatra_name = NAKSHATRAS[nakshatra_index][2]  # English name
    
    return nakshatra_num, pada, nakshatra_name, pada

# ---------------------------------------------------------------
# 8. லக்னம் (Lagna / Rising Sign) - எளிமைப்படுத்தப்பட்ட கணக்கீடு
# ---------------------------------------------------------------
def calculate_lagna(jd: float, latitude: float, longitude: float) -> int:
    """
    பிறந்த நேரத்தில் கிழக்கில் உதிக்கும் ராசியை கணக்கிடுகிறது.
    இது எளிமைப்படுத்தப்பட்ட கணக்கீடு.
    """
    # Universal Time
    # For a more accurate calculation, we'd need sidereal time calculation
    # This is a simplified approximation
    
    # Calculate the sidereal time at birth
    T = (jd - 2451545.0) / 36525.0
    
    # Greenwich Mean Sidereal Time at 0h UT
    gmst = 280.46061837 + 360.98564736629 * (jd - 2451545.0) + 0.000387933 * T * T - T * T * T / 38710000
    gmst = gmst % 360
    
    # Local Sidereal Time (simplified)
    lst = gmst + longitude  # Convert longitude to time
    lst = lst % 360
    
    # Approximate Lagna (this is a very simplified calculation)
    # In reality, this requires solving for the ascendant using oblique ascension
    lagna_approx = lst % 360
    
    # Apply ayanamsa
    ayanamsa = calculate_ayanamsa(jd)
    lagna_sidereal = (lagna_approx - ayanamsa) % 360
    
    lagna_rasi = get_rasi(lagna_sidereal)
    return lagna_rasi

# ---------------------------------------------------------------
# 9. விம்சோத்தரி தசா கணக்கீடு
# ---------------------------------------------------------------
def calculate_vimshottari_dasha(birth_jd: float, nakshatra_num: int, pada: int) -> list:
    """
    விம்சோத்தரி தசாவை கணக்கிடுகிறது.
    பிறந்த நட்சத்திரம் மற்றும் பாதத்திலிருந்து ஆரம்ப தசாவை தீர்மானிக்கிறது.
    """
    from utils.constants import DASHA_LORDS, VIMSHOTTARI_DASHA, NAKSHATRA_LORDS
    
    # Find the starting dasha lord based on nakshatra
    start_lord = NAKSHATRA_LORDS[nakshatra_num]
    
    # Find the index of the starting lord in the dasha sequence
    start_index = DASHA_LORDS.index(start_lord)
    
    # Calculate remaining years in the first dasha based on pada
    # Each nakshatra is 13.33 deg, each pada is 3.33 deg
    # The portion of dasha remaining = (4 - pada) / 4 * dasha_years
    dasha_years = VIMSHOTTARI_DASHA[start_lord]
    remaining_years = (4 - pada + 1) / 4 * dasha_years
    
    # Build the dasha sequence
    dashas = []
    current_year = 0
    
    # First dasha (remaining portion)
    if remaining_years > 0:
        dashas.append({
            "lord": start_lord,
            "lord_tamil": "",
            "total_years": dasha_years,
            "remaining_years": round(remaining_years, 2),
            "start_age": 0,
            "end_age": round(remaining_years, 2)
        })
        current_year = remaining_years
    
    # Subsequent dashas
    for i in range(1, 20):  # Cover multiple cycles
        lord_index = (start_index + i) % 9
        lord = DASHA_LORDS[lord_index]
        years = VIMSHOTTARI_DASHA[lord]
        
        dashas.append({
            "lord": lord,
            "lord_tamil": "",
            "total_years": years,
            "remaining_years": years,
            "start_age": round(current_year, 2),
            "end_age": round(current_year + years, 2)
        })
        current_year += years
    
    return dashas

# ---------------------------------------------------------------
# 10. பிறந்த தேதியிலிருந்து வயது கணக்கீடு
# ---------------------------------------------------------------
def calculate_age(birth_date: datetime, target_date: Optional[datetime] = None) -> float:
    """பிறந்த தேதியிலிருந்து வயதை கணக்கிடுகிறது."""
    if target_date is None:
        target_date = datetime.now()
    
    years = target_date.year - birth_date.year
    months = target_date.month - birth_date.month
    days = target_date.day - birth_date.day
    
    if days < 0:
        months -= 1
        # Get days in previous month
        if target_date.month == 1:
            prev_month = 12
            prev_year = target_date.year - 1
        else:
            prev_month = target_date.month - 1
            prev_year = target_date.year
        days_in_prev_month = (datetime(prev_year, prev_month + 1, 1) - datetime(prev_year, prev_month, 1)).days
        days += days_in_prev_month
    
    if months < 0:
        years -= 1
        months += 12
    
    age_years = years + months / 12 + days / 365.25
    return round(age_years, 2)

# ---------------------------------------------------------------
# 11. தேதியிலிருந்து JD கணக்கீடு (datetime object)
# ---------------------------------------------------------------
def datetime_to_jd(dt: datetime) -> float:
    """datetime object ஐ JD ஆக மாற்றுகிறது."""
    year = dt.year
    month = dt.month
    
    # Day with fraction
    day = dt.day + dt.hour / 24.0 + dt.minute / 1440.0 + dt.second / 86400.0
    
    return julian_day_number(year, month, day)
