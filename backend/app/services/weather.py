import httpx
from typing import Optional, Dict
from app.config import settings


class WeatherService:
    def __init__(self):
        self.api_key = settings.WEATHER_API_KEY
        self.base_url = settings.WEATHER_API_URL
    
    async def get_weather(self, location: str) -> Optional[Dict]:
        """Get current weather for a location"""
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "q": location,
                    "appid": self.api_key,
                    "units": "metric"
                }
                response = await client.get(self.base_url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                return {
                    "temperature": data.get("main", {}).get("temp"),
                    "condition": data.get("weather", [{}])[0].get("main", "").lower(),
                    "description": data.get("weather", [{}])[0].get("description"),
                    "humidity": data.get("main", {}).get("humidity"),
                    "wind_speed": data.get("wind", {}).get("speed"),
                    "location": location
                }
        except Exception as e:
            print(f"Weather API error: {e}")
            return None
    
    def get_outfit_suggestions_from_weather(self, temperature: float, condition: str) -> Dict:
        """Get outfit suggestions based on weather"""
        suggestions = {
            "layers": [],
            "materials": [],
            "accessories": []
        }
        
        if temperature < 5:
            suggestions["layers"] = ["coat", "jacket", "sweater"]
            suggestions["materials"] = ["wool", "fleece", "down"]
            suggestions["accessories"] = ["scarf", "gloves", "hat"]
        elif temperature < 15:
            suggestions["layers"] = ["jacket", "sweater", "blazer"]
            suggestions["materials"] = ["cotton", "wool", "denim"]
            suggestions["accessories"] = ["scarf", "light_jacket"]
        elif temperature < 25:
            suggestions["layers"] = ["light_jacket", "cardigan"]
            suggestions["materials"] = ["cotton", "linen"]
            suggestions["accessories"] = []
        else:
            suggestions["layers"] = ["t_shirt", "tank_top"]
            suggestions["materials"] = ["cotton", "linen", "breathable"]
            suggestions["accessories"] = ["sunglasses", "hat"]
        
        if condition in ["rain", "drizzle"]:
            suggestions["accessories"].append("umbrella")
            suggestions["materials"].append("waterproof")
        
        return suggestions


weather_service = WeatherService()
