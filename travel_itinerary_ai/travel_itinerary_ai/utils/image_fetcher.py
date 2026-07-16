import requests
import os
from typing import Dict, List
import re

# Using Unsplash API for free high-quality images
UNSPLASH_API_KEY = os.getenv("UNSPLASH_API_KEY", "demo")  # Get from environment or use demo
UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"

# Fallback: Using Pexels API (alternative free option)
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", None)
PEXELS_API_URL = "https://api.pexels.com/v1/search"

def fetch_place_image(place_name: str) -> str:
    """
    Fetch an image URL for a given place using Unsplash API
    Falls back to a default placeholder if API fails
    """
    try:
        # Clean up place name
        if not place_name or len(place_name.strip()) < 2:
            return "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=600&q=80"
        
        place_name = place_name.strip()
        
        # Try Unsplash API
        if UNSPLASH_API_KEY and UNSPLASH_API_KEY != "demo":
            params = {
                "query": place_name,
                "per_page": 1,
                "orientation": "landscape",
                "client_id": UNSPLASH_API_KEY
            }
            response = requests.get(UNSPLASH_API_URL, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("results"):
                    return data["results"][0]["urls"]["regular"]
        
        # Try Pexels API as fallback
        if PEXELS_API_KEY:
            headers = {"Authorization": PEXELS_API_KEY}
            params = {"query": place_name, "per_page": 1}
            response = requests.get(PEXELS_API_URL, params=params, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("photos"):
                    return data["photos"][0]["src"]["large"]
        
        # Use a generic travel image if no specific image found
        return f"https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=600&q=80"
    
    except Exception as e:
        # Return generic travel image on error
        return f"https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=600&q=80"

def extract_place_from_activity(activity_text: str) -> str:
    """
    Extract place name from activity text
    """
    if not activity_text:
        return None
    
    # Remove cost information and extra details
    text = activity_text.split("(")[0].strip()
    text = text.split("Cost:")[0].strip()
    
    # Split by colon and get the part before it (usually the attraction name)
    parts = text.split(":")
    if len(parts) > 0:
        place = parts[0].strip()
        # Remove leading asterisks and other formatting
        place = re.sub(r'^\*+', '', place).strip()
        if len(place) > 3:
            return place
    
    return None

def fetch_images_for_itinerary(days_breakdown: List[Dict]) -> List[Dict]:
    """
    Add image URLs to each day's data and individual activities
    """
    for day in days_breakdown:
        # Fetch image for the day's location
        if day.get("location"):
            day["image"] = fetch_place_image(day["location"])
        else:
            day["image"] = "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=600&q=80"
        
        # Add images for specific attractions mentioned in activities
        for activity in day.get("activities", []):
            activity["activity_items_with_images"] = []
            
            for item in activity.get("items", []):
                # Extract place name from activity
                place_name = extract_place_from_activity(item)
                
                item_data = {
                    "text": item,
                    "image": None
                }
                
                if place_name:
                    item_data["image"] = fetch_place_image(place_name)
                    item_data["place_name"] = place_name
                
                activity["activity_items_with_images"].append(item_data)
    
    return days_breakdown

