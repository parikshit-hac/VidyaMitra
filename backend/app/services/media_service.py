import requests
from typing import List, Dict, Optional
from app.settings import settings

class MediaService:
    def __init__(self):
        self.pexels_api_key = settings.pexels_api_key
        self.exchange_api_key = settings.exchange_api_key
    
    def search_images(self, query: str, per_page: int = 20) -> List[Dict]:
        """Search for images using Pexels API"""
        if not self.pexels_api_key:
            return self._get_fallback_images(query, per_page)
        
        try:
            headers = {
                "Authorization": self.pexels_api_key
            }
            
            url = "https://api.pexels.com/v1/search"
            params = {
                "query": query,
                "per_page": per_page,
                "orientation": "landscape"
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                images = []
                
                for photo in data.get("photos", []):
                    image_data = {
                        "id": photo["id"],
                        "url": photo["url"],
                        "photographer": photo["photographer"],
                        "photographerUrl": photo["photographer_url"],
                        "imageUrl": photo["src"]["large"],
                        "thumbnailUrl": photo["src"]["medium"],
                        "width": photo["width"],
                        "height": photo["height"],
                        "alt": photo.get("alt", query)
                    }
                    images.append(image_data)
                
                return images
            else:
                print(f"Pexels API error: {response.status_code} - {response.text}")
                return self._get_fallback_images(query, per_page)
                
        except Exception as e:
            print(f"Pexels service error: {e}")
            return self._get_fallback_images(query, per_page)
    
    def _get_fallback_images(self, query: str, per_page: int) -> List[Dict]:
        """Fallback images when Pexels API is unavailable"""
        
        # Career-related image placeholders
        career_images = {
            'office': [
                {
                    "id": 1,
                    "url": "https://www.pexels.com/search/office/",
                    "photographer": "Pexels Author",
                    "photographerUrl": "https://www.pexels.com",
                    "imageUrl": "https://via.placeholder.com/1200x800/4285F4/FFFFFF?text=Modern+Office",
                    "thumbnailUrl": "https://via.placeholder.com/400x300/4285F4/FFFFFF?text=Office",
                    "width": 1200,
                    "height": 800,
                    "alt": "Modern office workspace"
                },
                {
                    "id": 2,
                    "url": "https://www.pexels.com/search/workspace/",
                    "photographer": "Pexels Author",
                    "photographerUrl": "https://www.pexels.com",
                    "imageUrl": "https://via.placeholder.com/1200x800/34A853/FFFFFF?text=Workspace",
                    "thumbnailUrl": "https://via.placeholder.com/400x300/34A853/FFFFFF?text=Workspace",
                    "width": 1200,
                    "height": 800,
                    "alt": "Professional workspace"
                }
            ],
            'technology': [
                {
                    "id": 3,
                    "url": "https://www.pexels.com/search/technology/",
                    "photographer": "Pexels Author",
                    "photographerUrl": "https://www.pexels.com",
                    "imageUrl": "https://via.placeholder.com/1200x800/EA4335/FFFFFF?text=Technology",
                    "thumbnailUrl": "https://via.placeholder.com/400x300/EA4335/FFFFFF?text=Tech",
                    "width": 1200,
                    "height": 800,
                    "alt": "Technology and innovation"
                },
                {
                    "id": 4,
                    "url": "https://www.pexels.com/search/coding/",
                    "photographer": "Pexels Author",
                    "photographerUrl": "https://www.pexels.com",
                    "imageUrl": "https://via.placeholder.com/1200x800/FBBC04/000000?text=Coding",
                    "thumbnailUrl": "https://via.placeholder.com/400x300/FBBC04/000000?text=Coding",
                    "width": 1200,
                    "height": 800,
                    "alt": "Programming and coding"
                }
            ],
            'team': [
                {
                    "id": 5,
                    "url": "https://www.pexels.com/search/team/",
                    "photographer": "Pexels Author",
                    "photographerUrl": "https://www.pexels.com",
                    "imageUrl": "https://via.placeholder.com/1200x800/9C27B0/FFFFFF?text=Team+Work",
                    "thumbnailUrl": "https://via.placeholder.com/400x300/9C27B0/FFFFFF?text=Team",
                    "width": 1200,
                    "height": 800,
                    "alt": "Team collaboration"
                }
            ]
        }
        
        query_lower = query.lower()
        matched_images = []
        
        # Find matching images based on keywords
        for category, images in career_images.items():
            if category in query_lower:
                matched_images.extend(images)
        
        # If no specific match, provide general career images
        if not matched_images:
            matched_images = career_images['office']
        
        return matched_images[:per_page]
    
    def get_currency_rates(self, base_currency: str = "USD") -> Dict:
        """Get real currency exchange rates"""
        if not self.exchange_api_key:
            return self._get_fallback_rates(base_currency)
        
        try:
            url = f"https://v6.exchangerate-api.com/v6/{self.exchange_api_key}/latest/{base_currency}"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("result") == "success":
                    return {
                        "base": base_currency,
                        "rates": data.get("conversion_rates", {}),
                        "last_updated": data.get("time_last_update_unix", ""),
                        "success": True
                    }
                else:
                    print(f"Exchange API error: {data.get('error-type', 'Unknown error')}")
                    return self._get_fallback_rates(base_currency)
            else:
                print(f"Exchange API HTTP error: {response.status_code}")
                return self._get_fallback_rates(base_currency)
                
        except Exception as e:
            print(f"Exchange service error: {e}")
            return self._get_fallback_rates(base_currency)
    
    def _get_fallback_rates(self, base_currency: str) -> Dict:
        """Fallback exchange rates when API is unavailable"""
        
        # Realistic fallback rates (as of 2024)
        fallback_rates = {
            "USD": {
                "EUR": 0.92,
                "GBP": 0.79,
                "JPY": 149.50,
                "CAD": 1.36,
                "AUD": 1.53,
                "INR": 83.12,
                "CNY": 7.24,
                "CHF": 0.88,
                "SGD": 1.35
            },
            "EUR": {
                "USD": 1.09,
                "GBP": 0.86,
                "JPY": 162.89,
                "CAD": 1.48,
                "AUD": 1.67,
                "INR": 90.46,
                "CNY": 7.88,
                "CHF": 0.96,
                "SGD": 1.47
            },
            "GBP": {
                "USD": 1.27,
                "EUR": 1.16,
                "JPY": 189.44,
                "CAD": 1.72,
                "AUD": 1.94,
                "INR": 105.20,
                "CNY": 9.17,
                "CHF": 1.11,
                "SGD": 1.71
            }
        }
        
        rates = fallback_rates.get(base_currency, fallback_rates["USD"])
        
        return {
            "base": base_currency,
            "rates": rates,
            "last_updated": None,
            "success": True,
            "fallback": True
        }
    
    def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> Dict:
        """Convert currency amount"""
        
        rates_data = self.get_currency_rates(from_currency)
        
        if not rates_data.get("success"):
            return {
                "success": False,
                "error": "Unable to get exchange rates",
                "original_amount": amount,
                "from_currency": from_currency,
                "to_currency": to_currency
            }
        
        rates = rates_data.get("rates", {})
        
        if to_currency not in rates:
            return {
                "success": False,
                "error": f"Currency {to_currency} not supported",
                "original_amount": amount,
                "from_currency": from_currency,
                "to_currency": to_currency
            }
        
        converted_amount = amount * rates[to_currency]
        
        return {
            "success": True,
            "original_amount": amount,
            "converted_amount": round(converted_amount, 2),
            "from_currency": from_currency,
            "to_currency": to_currency,
            "exchange_rate": rates[to_currency],
            "fallback": rates_data.get("fallback", False)
        }

# Global media service instance
media_service = MediaService()
