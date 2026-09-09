"""
சுயவிவர மேலாண்மை - JSON அடிப்படையிலான தரவு சேமிப்பு
Profile management - JSON-based data storage
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class ProfileDatabase:
    """சுயவிவர தரவுத்தளம் - தனி நபர் தகவல்களை சேமிக்கிறது"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.profiles_file = self.data_dir / "profiles.json"
        self._load_profiles()
    
    def _load_profiles(self):
        """சேமித்த சுயவிவரங்களை ஏற்றுகிறது"""
        if self.profiles_file.exists():
            try:
                with open(self.profiles_file, "r", encoding="utf-8") as f:
                    self.profiles = json.load(f)
            except:
                self.profiles = {}
        else:
            self.profiles = {}
    
    def _save_profiles(self):
        """சுயவிவரங்களை சேமிக்கிறது"""
        with open(self.profiles_file, "w", encoding="utf-8") as f:
            json.dump(self.profiles, f, ensure_ascii=False, indent=2)
    
    def add_profile(self, profile_id: str, data: Dict) -> bool:
        """புதிய சுயவிவரத்தை சேர்க்கிறது"""
        try:
            self.profiles[profile_id] = data
            self._save_profiles()
            return True
        except:
            return False
    
    def get_profile(self, profile_id: str) -> Optional[Dict]:
        """சுயவிவரத்தை பெறுகிறது"""
        return self.profiles.get(profile_id)
    
    def update_profile(self, profile_id: str, data: Dict) -> bool:
        """சுயவிவரத்தை புதுப்பிக்கிறது"""
        if profile_id in self.profiles:
            self.profiles[profile_id].update(data)
            self._save_profiles()
            return True
        return False
    
    def delete_profile(self, profile_id: str) -> bool:
        """சுயவிவரத்தை நீக்குகிறது"""
        if profile_id in self.profiles:
            del self.profiles[profile_id]
            self._save_profiles()
            return True
        return False
    
    def list_profiles(self) -> List[Dict]:
        """அனைத்து சுயவிவரங்களையும் பட்டியலிடுகிறது"""
        return [
            {"id": pid, **info}
            for pid, info in self.profiles.items()
        ]
    
    def search_profiles(self, query: str) -> List[Dict]:
        """சுயவிவரங்களை தேடுகிறது"""
        results = []
        query = query.lower()
        for pid, info in self.profiles.items():
            if query in pid.lower() or query in info.get("name", "").lower():
                results.append({"id": pid, **info})
        return results
    
    def get_profile_count(self) -> int:
        """சுயவிவரங்களின் எண்ணிக்கை"""
        return len(self.profiles)
