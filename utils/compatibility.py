"""
திருமண பொருத்தம் கணிப்பு
Marriage compatibility matching system
"""
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from utils.constants import (
    NAKSHATRAS, NAKSHATRA_LORDS, RASI_TAMIL, PLANETS_TAMIL,
    PORUTHAM_LIST
)
from utils.vedic import BirthChart


class CompatibilityEngine:
    """திருமண பொருத்தம் கணிக்கும் இயந்திரம்"""
    
    def __init__(self, chart1: BirthChart, chart2: BirthChart,
                 name1: str = "நபர் 1", name2: str = "நபர் 2"):
        self.chart1 = chart1
        self.chart2 = chart2
        self.name1 = name1
        self.name2 = name2
    
    def calculate_porutham(self) -> Dict:
        """10 வகையான பொருத்தங்களையும் கணக்கிடுகிறது"""
        results = {}
        total_score = 0
        max_score = 0
        
        for porutham in PORUTHAM_LIST:
            name_tamil = porutham[0]
            name_english = porutham[1]
            description = porutham[2]
            max_marks = porutham[3]
            
            score = self._calculate_single_porutham(name_english)
            results[name_english] = {
                "name_tamil": name_tamil,
                "description": description,
                "score": score,
                "max_score": max_marks,
                "percentage": round((score / max_marks) * 100, 1) if max_marks > 0 else 0,
                "status": "பொருத்தம்" if score >= max_marks * 0.5 else "பொருந்தவில்லை"
            }
            
            total_score += score
            max_score += max_marks
        
        overall_pct = round((total_score / max_score) * 100, 1) if max_score > 0 else 0
        
        return {
            "details": results,
            "total_score": total_score,
            "max_score": max_score,
            "overall_percentage": overall_pct,
            "verdict": self._get_verdict(overall_pct),
            "total_poruthams": sum(1 for r in results.values() if r["status"] == "பொருத்தம்"),
            "total_poruthams_max": len(PORUTHAM_LIST)
        }
    
    def _calculate_single_porutham(self, porutham_type: str) -> int:
        """ஒவ்வொரு பொருத்தத்தையும் கணக்கிடுகிறது"""
        
        n1 = self.chart1.moon_nakshatra_num
        n2 = self.chart2.moon_nakshatra_num
        p1 = self.chart1.moon_pada
        p2 = self.chart2.moon_pada
        
        r1 = self.chart1.rasi_positions["Moon"]
        r2 = self.chart2.rasi_positions["Moon"]
        
        diff = abs(n1 - n2)
        if diff > 13:
            diff = 27 - diff
        
        if porutham_type == "Dina":
            # நட்சத்திர சுழற்சி பொருத்தம் - 27-ல் வகுபடும் எண்ணிக்கை
            count_27 = 0
            for i in range(1, 28, 2):
                if diff == i or diff == (27 - i):
                    count_27 += 1
            return 6 if count_27 > 0 else 3 if diff % 9 == 0 else 0
        
        elif porutham_type == "Gana":
            # கணம் பொருத்தம்
            gana1 = self._get_gana(n1)
            gana2 = self._get_gana(n2)
            if gana1 == gana2:
                return 6
            elif abs(gana1 - gana2) == 1:
                return 3
            else:
                return 0
        
        elif porutham_type == "Mahendra":
            # மைந்திரம் - நட்சத்திர வேறுபாடு 4, 7, 10, 13, 16, 19, 22, 25
            mahendra_nums = [4, 7, 10, 13, 16, 19, 22, 25]
            return 6 if diff in mahendra_nums else 0
        
        elif porutham_type == "Stree Deergha":
            # ஸ்திரீ தீர்கம்
            return 6 if n2 >= n1 else 3 if diff <= 13 else 0
        
        elif porutham_type == "Yoni":
            # யோனி பொருத்தம்
            yoni1 = self._get_yoni(n1)
            yoni2 = self._get_yoni(n2)
            yoni_friends = self._get_yoni_friendship()
            if yoni1 == yoni2:
                return 4
            elif (yoni1, yoni2) in yoni_friends:
                return 4
            elif (yoni2, yoni1) in yoni_friends:
                return 2
            else:
                return 0
        
        elif porutham_type == "Rasi":
            # ராசி பொருத்தம்
            if r1 == r2:
                return 5
            elif abs(r1 - r2) in [2, 4, 6, 8, 10]:
                return 3
            elif abs(r1 - r2) == 7:
                return 0
            else:
                return 2
        
        elif porutham_type == "Rasi Adhipati":
            # ராசி அதிபதி பொருத்தம்
            lord1 = self._get_rasi_lord(r1)
            lord2 = self._get_rasi_lord(r2)
            return 5 if lord1 == lord2 else 2
        
        elif porutham_type == "Nakshatra":
            # நட்சத்திர பொருத்தம்
            return 5 if n1 != n2 else 0
        
        elif porutham_type == "Vasiyam":
            # வசியம்
            vasya_pairs = self._get_vasya_pairs()
            return 2 if (r1, r2) in vasya_pairs else 0
        
        elif porutham_type == "Rajju":
            # ராஜ்ஜியம்
            rajju_groups = self._get_rajju_groups()
            group1 = None
            group2 = None
            for g, members in rajju_groups.items():
                if n1 in members:
                    group1 = g
                if n2 in members:
                    group2 = g
            return 2 if group1 != group2 else 0
        
        return 0
    
    def _get_gana(self, nakshatra_num: int) -> int:
        """தேவ (1), மனுஷ (2), ராக்ஷச (3) கணங்கள்"""
        deva = [1, 4, 7, 10, 13, 16, 19, 22, 25]
        manusha = [3, 5, 8, 11, 14, 17, 20, 23, 26]
        rakshasa = [2, 6, 9, 12, 15, 18, 21, 24, 27]
        
        if nakshatra_num in deva:
            return 1
        elif nakshatra_num in manusha:
            return 2
        else:
            return 3
    
    def _get_yoni(self, nakshatra_num: int) -> int:
        """யோனி வகைப்பாடு (1-14)"""
        yonis = {
            1: 1, 2: 14, 3: 2, 4: 13, 5: 3, 6: 12, 7: 4,
            8: 11, 9: 5, 10: 10, 11: 6, 12: 9, 13: 7,
            14: 8, 15: 1, 16: 14, 17: 2, 18: 13, 19: 3,
            20: 12, 21: 4, 22: 11, 23: 5, 24: 10, 25: 6,
            26: 9, 27: 7
        }
        return yonis.get(nakshatra_num, 0)
    
    def _get_yoni_friendship(self) -> set:
        """யோனி நட்பு ஜோடிகள்"""
        return {
            (1, 4), (2, 13), (3, 14), (5, 12), (6, 11),
            (7, 10), (8, 9)
        }
    
    def _get_rasi_lord(self, rasi: int) -> int:
        """ராசி நாதன்"""
        lords = {
            1: 1, 2: 2, 3: 3, 4: 4, 5: 1, 6: 3,
            7: 2, 8: 5, 9: 6, 10: 7, 11: 7, 12: 6
        }
        return lords.get(rasi, 0)
    
    def _get_vasya_pairs(self) -> set:
        """வசிய ராசி ஜோடிகள்"""
        return {
            (1, 5), (1, 9), (2, 6), (2, 10), (3, 7), (3, 11),
            (4, 8), (4, 12), (5, 9), (6, 10), (7, 11), (8, 12)
        }
    
    def _get_rajju_groups(self) -> Dict[str, List[int]]:
        """ராஜ்ஜிய குழுக்கள்"""
        return {
            "madhyama": [1, 7, 13, 19, 25],  # Middle
            "adho": [2, 8, 14, 20, 26],       # End
            "kesha": [3, 9, 15, 21, 27],      # Hair
            "urdhva": [4, 10, 16, 22],        # Head
            "madhya": [5, 11, 17, 23],        # Middle
            "anthya": [6, 12, 18, 24]         # End
        }
    
    def _get_verdict(self, percentage: float) -> Dict:
        """இறுதி முடிவு"""
        if percentage >= 80:
            return {
                "text": "மிகவும் நல்ல பொருத்தம்! திருமணத்திற்கு உகந்தது.",
                "emoji": "🟢",
                "level": "excellent"
            }
        elif percentage >= 65:
            return {
                "text": "நல்ல பொருத்தம். சில சிறிய சரிசெய்தல்களுடன் திருமணம் செய்துகொள்ளலாம்.",
                "emoji": "🟡",
                "level": "good"
            }
        elif percentage >= 50:
            return {
                "text": "சராசரி பொருத்தம். பரிகாரங்கள் செய்து திருமணம் செய்யலாம்.",
                "emoji": "🟠",
                "level": "average"
            }
        else:
            return {
                "text": "பொருத்தம் குறைவு. முழு ஜாதகங்களையும் ஆராய்ந்து முடிவெடுக்கவும்.",
                "emoji": "🔴",
                "level": "poor"
            }
    
    def generate_compatibility_report(self) -> Dict:
        """முழுமையான பொருத்த அறிக்கை"""
        porutham = self.calculate_porutham()
        
        # Additional analysis
        report = {
            "couple": {
                f"{self.name1}": self._person_summary(self.chart1),
                f"{self.name2}": self._person_summary(self.chart2)
            },
            "porutham": porutham,
            "strengths": self._find_strengths(porutham),
            "weaknesses": self._find_weaknesses(porutham),
            "remedies": self._suggest_remedies(porutham)
        }
        
        return report
    
    def _person_summary(self, chart: BirthChart) -> Dict:
        """நபர் சுருக்கம்"""
        return {
            "name": chart.name,
            "birth_date": chart.birth_date.strftime("%Y-%m-%d"),
            "moon_rasi": chart.rasi_positions.get("Moon", 0),
            "moon_nakshatra": chart.moon_nakshatra_name,
            "lagna": chart.lagna_rasi
        }
    
    def _find_strengths(self, porutham: Dict) -> List[str]:
        """பொருத்தத்தின் பலங்கள்"""
        strengths = []
        high_scorers = [p for p in porutham["details"].values() 
                       if p["percentage"] >= 75]
        for h in high_scorers[:3]:
            strengths.append(f"{h['name_tamil']} ({h['description']}) - {h['score']}/{h['max_score']}")
        return strengths
    
    def _find_weaknesses(self, porutham: Dict) -> List[str]:
        """பொருத்தத்தின் பலவீனங்கள்"""
        weaknesses = []
        low_scorers = [p for p in porutham["details"].values() 
                      if p["percentage"] < 50]
        for l in low_scorers[:3]:
            weaknesses.append(f"{l['name_tamil']} - {l['score']}/{l['max_score']}")
        return weaknesses
    
    def _suggest_remedies(self, porutham: Dict) -> List[str]:
        """பரிகாரங்கள்"""
        remedies = []
        if porutham["overall_percentage"] < 65:
            remedies.extend([
                "துலா பார்வதி தானம் செய்யவும்",
                "சந்திர தோஷத்திற்கு ருத்திராட்சம் அணியவும்",
                "வெள்ளிக்கிழமை விரதம் இருந்து அம்பாளை வழிபடவும்",
                "திருமணத்திற்கு முன் நவகிரக ஹோமம் செய்யவும்"
            ])
        return remedies
