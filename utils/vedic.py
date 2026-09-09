"""
வேத ஜோதிட கணக்கீடுகள்
Vedic astrology calculations
"""
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from utils.constants import (
    RASI_TAMIL, RASI_ENGLISH, NAKSHATRAS, PLANETS_TAMIL,
    NAKSHATRA_LORDS, DASHA_LORDS, VIMSHOTTARI_DASHA
)
from utils.calculator import (
    datetime_to_jd, sun_longitude, moon_longitude,
    planetary_positions, calculate_ayanamsa,
    sidereal_longitude, get_rasi, get_nakshatra_and_pada,
    calculate_lagna, calculate_vimshottari_dasha, calculate_age
)


class BirthChart:
    """ஜாதகம் - Individual birth chart"""
    
    def __init__(self, name: str, birth_date: datetime, birth_place: str = "",
                 latitude: float = 13.0, longitude: float = 80.0):
        self.name = name
        self.birth_date = birth_date
        self.birth_place = birth_place
        self.latitude = latitude
        self.longitude = longitude
        
        # Calculate chart data
        self.jd = datetime_to_jd(birth_date)
        self.ayanamsa = calculate_ayanamsa(self.jd)
        self.age = calculate_age(birth_date)
        
        # Calculate planetary positions
        self.tropical_positions = planetary_positions(self.jd)
        self.sidereal_positions = {}
        for planet, lon in self.tropical_positions.items():
            self.sidereal_positions[planet] = sidereal_longitude(lon, self.ayanamsa)
        
        # Calculate Rasi positions
        self.rasi_positions = {}
        for planet, lon in self.sidereal_positions.items():
            self.rasi_positions[planet] = get_rasi(lon)
        
        # Calculate Lagna
        self.lagna_rasi = calculate_lagna(self.jd, latitude, longitude)
        
        # Moon nakshatra
        moon_lon = self.sidereal_positions["Moon"]
        self.moon_nakshatra_num, self.moon_pada, self.moon_nakshatra_name, _ = get_nakshatra_and_pada(moon_lon)
        
        # Sun nakshatra
        sun_lon = self.sidereal_positions["Sun"]
        self.sun_nakshatra_num, self.sun_pada, self.sun_nakshatra_name, _ = get_nakshatra_and_pada(sun_lon)
        
        # Calculate Dasha
        self.dasha_sequence = calculate_vimshottari_dasha(self.jd, self.moon_nakshatra_num, self.moon_pada)
        
        # Determine current dasha
        self.current_dasha = self._get_current_dasha()
    
    def _get_current_dasha(self) -> Optional[Dict]:
        """தற்போதைய தசாவை கண்டுபிடிக்கிறது"""
        for dasha in self.dasha_sequence:
            if self.age >= dasha["start_age"] and self.age < dasha["end_age"]:
                # Calculate antardasha (sub-period)
                lord = dasha["lord"]
                main_years = dasha["total_years"]
                elapsed = self.age - dasha["start_age"]
                remaining = dasha["end_age"] - self.age
                
                # Find antardasha
                start_idx = DASHA_LORDS.index(lord)
                antardashas = []
                cum_time = 0
                for j in range(9):
                    sub_lord = DASHA_LORDS[(start_idx + j) % 9]
                    sub_years = VIMSHOTTARI_DASHA[sub_lord] * main_years / 120
                    sub_start = dasha["start_age"] + cum_time
                    sub_end = sub_start + sub_years
                    
                    antardashas.append({
                        "lord": sub_lord,
                        "start_age": round(sub_start, 2),
                        "end_age": round(sub_end, 2),
                        "years": round(sub_years, 2)
                    })
                    cum_time += sub_years
                
                # Find current antardasha
                current_antara = None
                for ad in antardashas:
                    if self.age >= ad["start_age"] and self.age < ad["end_age"]:
                        current_antara = ad
                        break
                
                dasha["antardashas"] = antardashas
                dasha["current_antardasha"] = current_antara
                dasha["elapsed"] = round(elapsed, 2)
                return dasha
        return None
    
    def get_nakshatra_details(self) -> Dict:
        """நட்சத்திர விவரங்களை தருகிறது"""
        details = {}
        
        nak_info = NAKSHATRAS[self.moon_nakshatra_num - 1]
        details["moon"] = {
            "nakshatra_num": self.moon_nakshatra_num,
            "nakshatra_tamil": nak_info[1],
            "nakshatra_english": nak_info[2],
            "pada": self.moon_pada,
            "lord": NAKSHATRA_LORDS[self.moon_nakshatra_num],
            "deity": nak_info[4]
        }
        
        nak_info_sun = NAKSHATRAS[self.sun_nakshatra_num - 1]
        details["sun"] = {
            "nakshatra_num": self.sun_nakshatra_num,
            "nakshatra_tamil": nak_info_sun[1],
            "nakshatra_english": nak_info_sun[2],
            "pada": self.sun_pada,
            "lord": NAKSHATRA_LORDS[self.sun_nakshatra_num],
            "deity": nak_info_sun[4]
        }
        
        return details
    
    def get_chart_summary(self) -> Dict:
        """ஜாதக சுருக்கத்தை தருகிறது"""
        return {
            "name": self.name,
            "birth_date": self.birth_date.strftime("%Y-%m-%d %H:%M"),
            "birth_place": self.birth_place,
            "age": self.age,
            "lagna_rasi": self.lagna_rasi,
            "lagna_rasi_tamil": RASI_TAMIL.get(self.lagna_rasi, ""),
            "lagna_rasi_english": RASI_ENGLISH.get(self.lagna_rasi, ""),
            "moon_rasi": self.rasi_positions["Moon"],
            "moon_rasi_tamil": RASI_TAMIL.get(self.rasi_positions["Moon"], ""),
            "sun_rasi": self.rasi_positions["Sun"],
            "sun_rasi_tamil": RASI_TAMIL.get(self.rasi_positions["Sun"], ""),
            "moon_nakshatra": self.moon_nakshatra_name,
            "moon_nakshatra_tamil": NAKSHATRAS[self.moon_nakshatra_num - 1][1],
            "current_dasha": self.current_dasha["lord"] if self.current_dasha else None
        }
    
    def get_planet_details(self) -> List[Dict]:
        """கிரக விவரங்களை தருகிறது"""
        details = []
        for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
            rasi = self.rasi_positions.get(planet, 0)
            details.append({
                "planet_english": planet,
                "planet_tamil": PLANETS_TAMIL.get(planet, ""),
                "sidereal_longitude": round(self.sidereal_positions.get(planet, 0), 2),
                "rasi": rasi,
                "rasi_tamil": RASI_TAMIL.get(rasi, ""),
                "rasi_english": RASI_ENGLISH.get(rasi, "")
            })
        return details
