import json
import os
from typing import Dict, Any, List
from datetime import datetime

class ProfileManager:
    def __init__(self, data_dir: str = "data/profiles"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.profile_file = os.path.join(data_dir, "user_profile.json")
        self.preferences_file = os.path.join(data_dir, "preferences.json")
        self.interactions_file = os.path.join(data_dir, "interactions.json")
    
    def create_profile(self, user_id: str, name: str, **kwargs) -> Dict[str, Any]:
        profile = {
            "user_id": user_id,
            "name": name,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "demographics": kwargs.get("demographics", {}),
            "interests": kwargs.get("interests", []),
            "skills": kwargs.get("skills", []),
            "goals": kwargs.get("goals", []),
            "communication_style": kwargs.get("communication_style", "neutral"),
            "learning_preferences": kwargs.get("learning_preferences", {})
        }
        
        with open(self.profile_file, 'w', encoding='utf-8') as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)
        
        return profile
    
    def get_profile(self) -> Dict[str, Any]:
        if not os.path.exists(self.profile_file):
            return {}
        
        with open(self.profile_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def update_profile(self, **updates) -> Dict[str, Any]:
        profile = self.get_profile()
        profile.update(updates)
        profile["updated_at"] = datetime.now().isoformat()
        
        with open(self.profile_file, 'w', encoding='utf-8') as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)
        
        return profile
    
    def add_interest(self, interest: str, weight: float = 1.0) -> None:
        profile = self.get_profile()
        interests = profile.get("interests", [])
        
        existing = next((item for item in interests if item.get("name") == interest), None)
        if existing:
            existing["weight"] += weight
        else:
            interests.append({"name": interest, "weight": weight, "added_at": datetime.now().isoformat()})
        
        self.update_profile(interests=interests)
    
    def add_skill(self, skill: str, level: str = "beginner") -> None:
        profile = self.get_profile()
        skills = profile.get("skills", [])
        
        existing = next((item for item in skills if item.get("name") == skill), None)
        if existing:
            existing["level"] = level
            existing["updated_at"] = datetime.now().isoformat()
        else:
            skills.append({
                "name": skill,
                "level": level,
                "added_at": datetime.now().isoformat()
            })
        
        self.update_profile(skills=skills)
    
    def set_preferences(self, preferences: Dict[str, Any]) -> None:
        current_prefs = self.get_preferences()
        current_prefs.update(preferences)
        current_prefs["updated_at"] = datetime.now().isoformat()
        
        with open(self.preferences_file, 'w', encoding='utf-8') as f:
            json.dump(current_prefs, f, ensure_ascii=False, indent=2)
    
    def get_preferences(self) -> Dict[str, Any]:
        if not os.path.exists(self.preferences_file):
            return {}
        
        with open(self.preferences_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def log_interaction(self, interaction_type: str, content: str, response: str = None, metadata: Dict = None) -> None:
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "type": interaction_type,
            "content": content,
            "response": response,
            "metadata": metadata or {}
        }
        
        interactions = []
        if os.path.exists(self.interactions_file):
            with open(self.interactions_file, 'r', encoding='utf-8') as f:
                interactions = json.load(f)
        
        interactions.append(interaction)
        
        # Keep only last 1000 interactions
        if len(interactions) > 1000:
            interactions = interactions[-1000:]
        
        with open(self.interactions_file, 'w', encoding='utf-8') as f:
            json.dump(interactions, f, ensure_ascii=False, indent=2)
    
    def get_interactions(self, limit: int = 100) -> List[Dict[str, Any]]:
        if not os.path.exists(self.interactions_file):
            return []
        
        with open(self.interactions_file, 'r', encoding='utf-8') as f:
            interactions = json.load(f)
        
        return interactions[-limit:] if limit else interactions
    
    def analyze_patterns(self) -> Dict[str, Any]:
        interactions = self.get_interactions(limit=None)
        profile = self.get_profile()
        
        if not interactions:
            return {"message": "No interactions to analyze"}
        
        # Analyze interaction patterns
        types = {}
        recent_topics = []
        
        for interaction in interactions[-50:]:  # Last 50 interactions
            itype = interaction.get("type", "unknown")
            types[itype] = types.get(itype, 0) + 1
            
            if interaction.get("metadata", {}).get("topics"):
                recent_topics.extend(interaction["metadata"]["topics"])
        
        return {
            "total_interactions": len(interactions),
            "interaction_types": types,
            "recent_topics": list(set(recent_topics)),
            "profile_completeness": self._calculate_completeness(profile)
        }
    
    def _calculate_completeness(self, profile: Dict[str, Any]) -> float:
        required_fields = ["name", "interests", "skills", "goals", "communication_style"]
        filled_fields = sum(1 for field in required_fields if profile.get(field))
        return filled_fields / len(required_fields)