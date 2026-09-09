"""
கணிப்பு இயந்திரம்
Prediction engine - generates clear predictions for any time period
"""
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
from utils.constants import (
    DASHA_PREDICTIONS, AGE_BASED_PREDICTIONS, PLANETS_TAMIL,
    DASHA_LORDS, VIMSHOTTARI_DASHA, PLANET_SIGNFICANCE
)
from utils.vedic import BirthChart


class PredictionEngine:
    """கணிப்பு இயந்திரம் - வெவ்வேறு காலகட்டங்களுக்கு தெளிவான கணிப்புகளை வழங்குகிறது"""
    
    def __init__(self, birth_chart: BirthChart):
        self.chart = birth_chart
    
    def generate_current_predictions(self) -> Dict:
        """தற்போதைய நிலைக்கான முழுமையான கணிப்புகள்"""
        predictions = {}
        
        # 1. தற்போதைய தசா கணிப்புகள்
        predictions["dasha"] = self._predict_from_dasha()
        
        # 2. வயது அடிப்படை கணிப்புகள்
        predictions["age"] = self._predict_from_age()
        
        # 3. ராசி அடிப்படை கணிப்புகள்
        predictions["rasi"] = self._predict_from_rasi()
        
        # 4. நட்சத்திர கணிப்புகள்
        predictions["nakshatra"] = self._predict_from_nakshatra()
        
        # 5. ஒருங்கிணைந்த முழுமையான கணிப்பு
        predictions["overall"] = self._generate_overall_prediction()
        
        return predictions
    
    def generate_future_predictions(self, years_ahead: int = 1) -> Dict:
        """எதிர்கால கணிப்புகள் - எத்தனை வருடங்கள் வேண்டுமானாலும் தெளிவாக கணிக்கும்"""
        predictions = {}
        
        # Get dashas covering the requested period
        future_dashas = self._get_future_dashas(years_ahead)
        predictions["dasha_periods"] = future_dashas
        
        # Year-by-year predictions
        yearly = {}
        for year_offset in range(years_ahead):
            target_age = self.chart.age + year_offset
            pred = self._predict_for_specific_age(target_age, year_offset)
            yearly[f"year_{year_offset}"] = pred
        
        predictions["yearly"] = yearly
        
        # Generate a consolidated future prediction
        predictions["summary"] = self._generate_future_summary(future_dashas, years_ahead)
        
        return predictions
    
    def _predict_from_dasha(self) -> Dict:
        """தசாவிலிருந்து கணிப்புகள்"""
        current = self.chart.current_dasha
        if not current:
            return {"status": "தசா தகவல் இல்லை"}
        
        lord = current["lord"]
        lord_tamil = PLANETS_TAMIL.get(lord, lord)
        pred_data = DASHA_PREDICTIONS.get(lord, {})
        
        # Antardasha info
        antara = current.get("current_antardasha", {})
        antara_lord = antara.get("lord", "")
        antara_tamil = PLANETS_TAMIL.get(antara_lord, antara_lord)
        
        result = {
            "main_dasha": {
                "lord": lord,
                "lord_tamil": lord_tamil,
                "start_age": current["start_age"],
                "end_age": current["end_age"],
                "elapsed": current["elapsed"],
                "remaining": round(current["end_age"] - self.chart.age, 2)
            },
            "antardasha": {
                "lord": antara_lord,
                "lord_tamil": antara_tamil,
                "start_age": antara.get("start_age"),
                "end_age": antara.get("end_age")
            } if antara else None,
            "positive": pred_data.get("positive", "நல்ல பலன்கள் கிடைக்கும் காலம்."),
            "negative": pred_data.get("negative", "எச்சரிக்கை தேவை."),
            "career": pred_data.get("career", "தொழில் வாய்ப்புகள் உண்டு."),
            "finance": pred_data.get("finance", "நிதி நிலை கவனம் தேவை."),
            "health": pred_data.get("health", "உடல் நலம் பேண வேண்டும்.")
        }
        
        # Add antardasha specific prediction
        if antara_lord and antara_lord in DASHA_PREDICTIONS:
            antara_pred = DASHA_PREDICTIONS[antara_lord]
            result["antardasha_effect"] = (
                f"தற்போதைய பூர்த்தி தசையில் {antara_tamil} பங்கு முக்கியம். "
                f"{antara_pred.get('positive', '')} "
                f"எச்சரிக்கை: {antara_pred.get('negative', '')}"
            )
        
        return result
    
    def _predict_from_age(self) -> Dict:
        """வயதிலிருந்து பொது கணிப்புகள்"""
        age = self.chart.age
        
        for (age_start, age_end), pred in AGE_BASED_PREDICTIONS.items():
            if age_start <= age < age_end:
                return {
                    "age_group": f"{age_start}-{age_end}",
                    "prediction": pred,
                    "details": self._get_age_specific_details(age)
                }
        
        return {
            "age_group": "60+",
            "prediction": AGE_BASED_PREDICTIONS.get((60, 100), ""),
            "details": self._get_age_specific_details(age)
        }
    
    def _get_age_specific_details(self, age: float) -> Dict:
        """வயது சார்ந்த விரிவான விவரங்கள்"""
        details = {}
        
        # Rasi-based age effects
        sun_rasi = self.chart.rasi_positions.get("Sun", 0)
        moon_rasi = self.chart.rasi_positions.get("Moon", 0)
        
        # Transit effects (simplified)
        if age < 30:
            details["focus"] = "கல்வி, தொழில் ஆரம்பம், திருமணம்"
        elif age < 45:
            details["focus"] = "தொழில் வளர்ச்சி, குடும்ப பொறுப்புகள், முதலீடு"
        elif age < 60:
            details["focus"] = "குழந்தைகள் எதிர்காலம், நிதி நிலைத்தன்மை, உடல் நலம்"
        else:
            details["focus"] = "ஓய்வு, ஆன்மிகம், சேவை"
        
        # Planetary period influences
        current_dasha_lord = self.chart.current_dasha["lord"] if self.chart.current_dasha else ""
        details["current_influence"] = f"{PLANETS_TAMIL.get(current_dasha_lord, current_dasha_lord)} பருவம்"
        
        return details
    
    def _predict_from_rasi(self) -> Dict:
        """ராசி அடிப்படை கணிப்புகள்"""
        from utils.constants import RASI_TAMIL
        
        moon_rasi = self.chart.rasi_positions.get("Moon", 0)
        sun_rasi = self.chart.rasi_positions.get("Sun", 0)
        lagna = self.chart.lagna_rasi
        
        return {
            "lagna": {
                "rasi": lagna,
                "name_tamil": RASI_TAMIL.get(lagna, ""),
                "meaning": self._get_lagna_meaning(lagna)
            },
            "moon_rasi": {
                "rasi": moon_rasi,
                "name_tamil": RASI_TAMIL.get(moon_rasi, ""),
                "meaning": self._get_moon_rasi_meaning(moon_rasi)
            },
            "sun_rasi": {
                "rasi": sun_rasi,
                "name_tamil": RASI_TAMIL.get(sun_rasi, ""),
                "influence": self._get_sun_rasi_influence(sun_rasi)
            }
        }
    
    def _get_lagna_meaning(self, rasi: int) -> str:
        """லக்ன ராசியின் பொருள்"""
        meanings = {
            1: "தைரியமான, சுதந்திரமான தன்மை. தலைமைத்துவம் உண்டு.",
            2: "நிலையான, பொறுமையான தன்மை. குடும்ப பாசம் அதிகம்.",
            3: "புத்திசாலி, தகவல் தொடர்பு திறன். பல நண்பர்கள்.",
            4: "உணர்ச்சிவசப்பட்ட, பாதுகாப்பு உணர்வு அதிகம். தாய் பாசம்.",
            5: "ஆடம்பர, அதிகார தன்மை. நாடக குணம் உண்டு.",
            6: "ஆராய்ச்சி மனப்பான்மை, சேவை உணர்வு. விமர்சன திறன்.",
            7: "சமநிலை, நீதி உணர்வு. பேச்சு திறன் மற்றும் கலை ஆர்வம்.",
            8: "ஆழ்ந்த சிந்தனை, மர்ம குணம். ஆராய்ச்சி திறன்.",
            9: "நேர்மை, தத்துவ ஆர்வம். பயணம் மற்றும் அறிவு விரிவு.",
            10: "லட்சியம், கடின உழைப்பு. பொறுப்புணர்வு அதிகம்.",
            11: "புதுமை ஆர்வம், நட்பு வட்டம். சுதந்திர ஆர்வம்.",
            12: "ஆன்மிக உணர்வு, தியான குணம். இரக்கம் மற்றும் ஞானம்."
        }
        return meanings.get(rasi, "பொதுவான தன்மை.")
    
    def _get_moon_rasi_meaning(self, rasi: int) -> str:
        """சந்திர ராசியின் பொருள்"""
        meanings = {
            1: "மனம் வேகமாக மாறும். உணர்ச்சி மிகுந்த தன்மை.",
            2: "நிலையான மனநிலை. சுகபோக ஆர்வம்.",
            3: "ஆர்வமான, ஆயாசமான மனநிலை. பேச்சு திறன்.",
            4: "உணர்ச்சி மிகுந்த, பாதுகாப்பு உணர்வு. தாய் மீது பற்று.",
            5: "நாடக தன்மை, புகழ் ஆசை. நெருங்கிய உறவுகளில் ஈடுபாடு.",
            6: "ஆராய்ச்சி மனப்பான்மை. உடல் நலம் மீது கவனம்.",
            7: "சமநிலை மனநிலை. உறவுகளில் முக்கியத்துவம்.",
            8: "மர்ம மனநிலை. ஆன்மிக ஆர்வம். தனிமை விருப்பம்.",
            9: "நேர்மை, தத்துவ சிந்தனை. பயண ஆர்வம்.",
            10: "லட்சிய மனநிலை. பொறுப்புணர்வு. அதிகார ஆசை.",
            11: "சுதந்திர ஆர்வம். நட்பு முக்கியம். புதுமை ஆர்வம்.",
            12: "ஆன்மிக மனநிலை. தியானம், யோகா ஆர்வம்."
        }
        return meanings.get(rasi, "பொதுவான மனநிலை.")
    
    def _get_sun_rasi_influence(self, rasi: int) -> str:
        """சூரிய ராசியின் செல்வாக்கு"""
        influences = {
            1: "தலைமைத்துவம், சுதந்திர ஆர்வம், அகங்காரம்.",
            2: "நிலையான முயற்சி, பொருள் சேர்க்கும் திறன்.",
            3: "தகவல் தொடர்பு திறன், சகோதர பாசம்.",
            4: "வீடு, குடும்பம் மீது அக்கறை. தாய் வழி செல்வாக்கு.",
            5: "படைப்பு திறன், குழந்தைகள் மீது ஆர்வம்.",
            6: "சேவை மனப்பான்மை, எதிரிகளை வெல்லும் திறன்.",
            7: "கூட்டு முயற்சி, திருமண வாழ்க்கை முக்கியம்.",
            8: "ஆழ்ந்த ஆராய்ச்சி, மர்ம விஷயங்களில் ஆர்வம்.",
            9: "அதிர்ஷ்டம், தந்தை வழி நன்மைகள், ஆன்மிகம்.",
            10: "தொழில் வெற்றி, சமூக அந்தஸ்து, புகழ்.",
            11: "நட்பு வட்டம், விருப்பங்கள் நிறைவேறும்.",
            12: "செலவு, வெளிநாடு, ஆன்மிக தேடல்."
        }
        return influences.get(rasi, "பொதுவான செல்வாக்கு.")
    
    def _predict_from_nakshatra(self) -> Dict:
        """நட்சத்திர அடிப்படை கணிப்புகள்"""
        from utils.constants import NAKSHATRAS
        
        nak = self.chart.get_nakshatra_details()
        moon_nak = nak["moon"]
        sun_nak = nak["sun"]
        
        # Nakshatra characteristics
        nak_index = moon_nak["nakshatra_num"] - 1
        nak_data = NAKSHATRAS[nak_index]
        
        # Nakshatra characteristics based on type
        characteristics = self._get_nakshatra_characteristics(moon_nak["nakshatra_num"])
        
        return {
            "birth_nakshatra": {
                "name": moon_nak["nakshatra_tamil"],
                "name_english": moon_nak["nakshatra_english"],
                "pada": moon_nak["pada"],
                "lord": moon_nak["lord"],
                "deity": nak_data[4]
            },
            "characteristics": characteristics,
            "sun_nakshatra": {
                "name": sun_nak["nakshatra_tamil"],
                "pada": sun_nak["pada"],
                "effect": self._get_sun_nakshatra_effect(sun_nak["nakshatra_num"])
            }
        }
    
    def _get_nakshatra_characteristics(self, nak_num: int) -> Dict:
        """நட்சத்திர குணாதிசயங்கள்"""
        # Simple mapping based on nakshatra type
        char_map = {
            1: "வைத்திய திறன், வேகமான செயல்பாடு, குதிரை போன்ற தன்மை.",
            2: "கண்டிப்பு, நீதி உணர்வு, சுமந்து செல்லும் தன்மை.",
            3: "தலைமைத்துவம், வெட்டும் திறன், கூர்மையான புத்தி.",
            4: "அழகு, படைப்பு திறன், சமூக தன்மை, வண்டி போன்று இழுத்துச் செல்லும்.",
            5: "தேடல், ஆர்வம், மிருகம் போன்று சுறுசுறுப்பு.",
            6: "துக்கம், கடின உழைப்பு, அழுகை போன்ற சோகம்.",
            7: "மீண்டும் எழும் தன்மை, நெகிழ்வு, இரண்டு முறை பிறப்பது போல.",
            8: "வளர்ப்பு, பாதுகாப்பு, பால் போன்று வளர்க்கும் தன்மை.",
            9: "சுருண்ட, மறைந்த, ஆழ்ந்த அறிவு, பாம்பு போன்று நெளியும்.",
            10: "பெரிய, முக்கியமான, அரச குடும்பம் போன்ற தன்மை.",
            11: "முந்தைய, பழமையான, மரம் போன்று ஆழ்ந்த வேர்கள்.",
            12: "பிற்பட்ட, உயர்ந்த, மரத்தின் உச்சி போன்று உயர்ந்த.",
            13: "கை போன்று பிடிக்கும் திறன், வேலை செய்யும் தன்மை.",
            14: "அழகான, மின்னும், நகை போன்று பிரகாசம்.",
            15: "சுதந்திரமான, நகரும், காற்று போன்று சுதந்திரம்.",
            16: "இரண்டு கிளைகள், பிரிவு, வழி பிரியும் தன்மை.",
            17: "பின் தொடரும், நட்பு, நட்சத்திரம் போன்று ஒளிரும்.",
            18: "மூத்த, தலைமையான, மூத்தவர் போன்ற கம்பீரம்.",
            19: "வேர், அடிப்படை, அழிக்கும் தன்மை, மூலம்.",
            20: "முந்தைய வெற்றி, ஆரம்ப வெற்றி, வெற்றி கொடி.",
            21: "பிற்பட்ட வெற்றி, பின்னர் வரும் வெற்றி.",
            22: "கேட்கும் தன்மை, கற்றல், காது போன்று கேட்கும்.",
            23: "இசை, செல்வம், மேளம் போன்று ஒலிக்கும்.",
            24: "மருத்துவம், குணப்படுத்தும், நூறு மருந்துகள்.",
            25: "முந்தைய அதிர்ஷ்டம், முன் வரும் நல்லது.",
            26: "பிற்பட்ட அதிர்ஷ்டம், பின் வரும் நல்லது.",
            27: "செல்வம், வளம், மீன் போன்று நீந்தும் தன்மை."
        }
        return {"characteristic": char_map.get(nak_num, "பொதுவான நட்சத்திர குணம்.")}
    
    def _get_sun_nakshatra_effect(self, nak_num: int) -> str:
        """சூரிய நட்சத்திரத்தின் விளைவு"""
        effects = {
            1: "ஆன்மா வலிமையானது. தலைமைத்துவம் இயற்கையாக வரும்.",
            2: "வாழ்க்கையில் சுமைகள் இருக்கும். பொறுமை முக்கியம்.",
            3: "தீர்மானமான செயல்பாடு. வெற்றி நிச்சயம்.",
            4: "மன அமைதி மற்றும் செல்வம் இரண்டும் வரும்.",
            5: "ஆராய்ச்சி முடிவுகள் நல்லது. கடின உழைப்பு பலன் தரும்.",
            6: "உணர்வுகள் ஆழமானது. கலை திறன் உண்டு.",
            7: "புதிய ஆரம்பங்கள். வீடு மாற்றம் வரலாம்.",
            8: "உறவுகளில் நெருக்கம். குடும்ப விரிவு.",
            9: "நல்ல அதிர்ஷ்ட காலம். புதிய வாய்ப்புகள்.",
            10: "தொழில் முன்னேற்றம். சமூக அங்கீகாரம்.",
            11: "விருப்பங்கள் நிறைவேறும். நண்பர்கள் உதவி.",
            12: "ஆன்மிக வளர்ச்சி. தியானம் பலன் தரும்.",
            13: "படைப்பு திறன் உச்சம். பணி முன்னேற்றம்.",
            14: "சுகபோக ஆசை அதிகம். எச்சரிக்கை தேவை.",
            15: "சுதந்திரம் முக்கியம். பயணம் வரும்.",
            16: "இரட்டை முடிவுகள். கவனமாக சிந்திக்க வேண்டும்.",
            17: "நட்பு பலன் தரும். கூட்டு முயற்சி வெற்றி.",
            18: "பொறுப்பு அதிகரிக்கும். தலைமை வகிக்கும் வாய்ப்பு.",
            19: "ஆழ்ந்த மாற்றங்கள். பழைய விஷயங்கள் முடிவு.",
            20: "ஆரம்ப முயற்சிகள் வெற்றி. உற்சாகம் தேவை.",
            21: "தாமதமான வெற்றி. பொறுமை முக்கியம்.",
            22: "கற்றல் மற்றும் பயணம். அறிவு விரிவு.",
            23: "செல்வம் மற்றும் இசை. வசதி வாய்ப்புகள்.",
            24: "மருத்துவ துறை வெற்றி. சேவை மனப்பான்மை.",
            25: "பூர்வ ஜென்ம கர்மா. ஆன்மிக முன்னேற்றம்.",
            26: "ஆழ்ந்த ஞானம். தியானம் பலன் தரும்.",
            27: "செல்வமும் சுகமும். குடும்ப மகிழ்ச்சி."
        }
        return effects.get(nak_num, "பொதுவான விளைவு.")
    
    def _generate_overall_prediction(self) -> Dict:
        """ஒருங்கிணைந்த முழுமையான கணிப்பு"""
        current = self.chart.current_dasha
        if not current:
            return {"prediction": "தசா தகவல் இல்லை"}
        
        lord = current["lord"]
        lord_tamil = PLANETS_TAMIL.get(lord, lord)
        
        # Combine dasha, age, and planetary influences
        dasha_pred = DASHA_PREDICTIONS.get(lord, {})
        
        # Generate a comprehensive prediction
        remaining_years = round(current["end_age"] - self.chart.age, 1)
        
        prediction = (
            f"**தற்போதைய நிலை:** உங்கள் {self.chart.age} வயதில் {lord_tamil} தசா நடைபெறுகிறது. "
            f"இந்த தசா இன்னும் {remaining_years} ஆண்டுகள் தொடரும்.\n\n"
            
            f"**முக்கிய விளைவுகள்:** {dasha_pred.get('positive', '')}\n\n"
            
            f"**எச்சரிக்கைகள்:** {dasha_pred.get('negative', '')}\n\n"
            
            f"**தொழில்:** {dasha_pred.get('career', '')}\n\n"
            
            f"**நிதி:** {dasha_pred.get('finance', '')}\n\n"
            
            f"**உடல் நலம்:** {dasha_pred.get('health', '')}\n\n"
            
            f"**வயது பரிந்துரை:** {self._get_age_advice()}"
        )
        
        return {
            "prediction": prediction,
            "summary_points": [
                f"✅ {lord_tamil} தசா - {dasha_pred.get('positive', '')[:50]}...",
                f"⚠️ {dasha_pred.get('negative', '')[:50]}...",
                f"💼 {dasha_pred.get('career', '')[:50]}..."
            ],
            "current_dasha": lord,
            "remaining_years": remaining_years,
            "age": self.chart.age
        }
    
    def _get_age_advice(self) -> str:
        """வயது சார்ந்த ஆலோசனை"""
        age = self.chart.age
        if age < 18:
            return "கல்வியில் கவனம் செலுத்துங்கள். பெற்றோர் ஆலோசனை முக்கியம்."
        elif age < 25:
            return "கல்வி மற்றும் தொழில் ஆரம்பத்தில் கவனம். உறவுகளை வலுப்படுத்துங்கள்."
        elif age < 35:
            return "தொழில் வளர்ச்சி மற்றும் நிதி திட்டமிடல் முக்கியம். திருமணம் பற்றி சிந்திக்கும் காலம்."
        elif age < 45:
            return "குடும்ப பொறுப்புகள் மற்றும் முதலீடுகளில் கவனம். உடல் நலத்தை பேணுங்கள்."
        elif age < 60:
            return "குழந்தைகள் எதிர்காலம் மற்றும் ஓய்வு திட்டமிடல். ஆன்மிகத்தில் ஆர்வம் வரும்."
        else:
            return "உடல் நலம் மற்றும் ஆன்மிகம் முக்கியம். அமைதியான வாழ்க்கை வாழுங்கள்."
    
    def _get_future_dashas(self, years_ahead: int) -> List[Dict]:
        """எதிர்கால தசா காலங்களை கணிக்கிறது"""
        future_dashas = []
        current_age = self.chart.age
        target_age = current_age + years_ahead
        
        for dasha in self.chart.dasha_sequence:
            if dasha["start_age"] >= current_age and dasha["start_age"] < target_age:
                lord = dasha["lord"]
                pred = DASHA_PREDICTIONS.get(lord, {})
                
                entry = {
                    "lord": lord,
                    "lord_tamil": PLANETS_TAMIL.get(lord, lord),
                    "start_age": dasha["start_age"],
                    "end_age": dasha["end_age"],
                    "years": dasha["total_years"],
                    "prediction": pred.get("positive", ""),
                    "caution": pred.get("negative", "")
                }
                future_dashas.append(entry)
            
            if dasha["start_age"] >= target_age:
                break
        
        return future_dashas
    
    def _predict_for_specific_age(self, target_age: float, year_offset: int) -> Dict:
        """ஒரு குறிப்பிட்ட வயதுக்கான கணிப்பு"""
        # Find the dasha for this age
        for dasha in self.chart.dasha_sequence:
            if dasha["start_age"] <= target_age < dasha["end_age"]:
                lord = dasha["lord"]
                pred = DASHA_PREDICTIONS.get(lord, {})
                
                # Calculate the progress within this dasha
                progress = (target_age - dasha["start_age"]) / dasha["total_years"]
                
                year = datetime.now().year + year_offset
                
                return {
                    "year": year,
                    "age": target_age,
                    "dasha": lord,
                    "dasha_tamil": PLANETS_TAMIL.get(lord, lord),
                    "progress_pct": round(progress * 100, 1),
                    "prediction": pred.get("positive", ""),
                    "caution": pred.get("negative", ""),
                    "focus": self._get_focus_for_age(target_age)
                }
        
        return {"year": datetime.now().year + year_offset, "age": target_age, "prediction": "தசா தகவல் இல்லை"}
    
    def _get_focus_for_age(self, age: float) -> str:
        """வயதுக்கு ஏற்ற கவனம்"""
        if age < 18: return "கல்வி"
        elif age < 25: return "கல்வி, தொழில்"
        elif age < 35: return "தொழில், திருமணம், நிதி"
        elif age < 45: return "தொழில், குடும்பம், முதலீடு"
        elif age < 60: return "நிதி, குழந்தைகள், உடல்நலம்"
        else: return "உடல்நலம், ஆன்மிகம், சேவை"
    
    def _generate_future_summary(self, future_dashas: List[Dict], years_ahead: int) -> str:
        """எதிர்கால சுருக்கம்"""
        if not future_dashas:
            return "எதிர்கால தசா தகவல் இல்லை."
        
        current_age = self.chart.age
        summary_parts = [
            f"## 🔮 அடுத்த {years_ahead} ஆண்டுகளுக்கான முழுமையான கணிப்பு\n",
            f"**தற்போதைய வயது:** {current_age}\n",
            f"**கணிப்பு காலம்:** {datetime.now().year} முதல் {datetime.now().year + years_ahead} வரை\n",
            "---\n"
        ]
        
        for i, d in enumerate(future_dashas):
            summary_parts.append(f"### 📅 பருவம் {i+1}: {d['lord_tamil']} தசா")
            summary_parts.append(f"**காலம்:** வயது {d['start_age']} முதல் {d['end_age']} வரை ({d['years']} ஆண்டுகள்)")
            summary_parts.append(f"**நல்ல பலன்கள்:** {d['prediction']}")
            summary_parts.append(f"**எச்சரிக்கை:** {d['caution']}")
            summary_parts.append("")
        
        summary_parts.append("---")
        summary_parts.append("### 💡 முக்கிய ஆலோசனைகள்")
        summary_parts.append("1. ஒவ்வொரு தசாவும் வாழ்க்கையில் புதிய அனுபவங்களை தரும்.")
        summary_parts.append("2. கிரகங்களின் நிலைக்கு ஏற்ப முடிவுகளை எடுக்கவும்.")
        summary_parts.append("3. சுப கிரகங்களின் காலத்தில் முக்கிய முடிவுகளை எடுக்கவும்.")
        summary_parts.append("4. நிதி திட்டமிடல் மற்றும் உடல் நலத்தில் எச்சரிக்கையாக இருக்கவும்.")
        summary_parts.append("5. ஆன்மிக பயிற்சிகள் மற்றும் தான தர்மங்கள் நல்ல பலன்களை தரும்.")
        
        return "\n".join(summary_parts)
