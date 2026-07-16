import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY not found in .env file")

# Debug: check if key is loaded
print(f"API Key loaded: {api_key[:20]}..." if api_key else "No API key found")

client = Groq(api_key=api_key)

def generate_itinerary(city, days, budget):
    try:
        prompt = f"""Create a detailed {days}-day travel itinerary for {city} with a budget of {budget}.

IMPORTANT INSTRUCTIONS:
1. Focus ONLY on historical landmarks and cultural sites
2. For each day:
   - List the day title/theme
   - Morning activities (with specific places only)
   - Afternoon activities (with specific places only)
   - Evening activities (with specific places only)
   - Night activities/dining
   - Estimated total cost for that day (ONE number only - NOT per activity)

3. Include entry fees in the total daily cost
4. NO duplicate costs - show cost breakdown ONLY at the end of each day
5. Format clearly with "Day 1:", "Day 2:", etc.

COST FORMAT:
Estimated costs for Day X: ₹XXXX-XXXX (one consolidated cost only)

Do NOT repeat costs for individual landmarks.
Focus on historical monuments, temples, ancient sites, museums, historical buildings."""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.7
        )

        return response.choices[0].message.content
    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "invalid_api_key" in error_msg.lower():
            return "❌ Invalid Groq API Key. Please verify your API key at https://console.groq.com/keys"
        elif "rate_limit" in error_msg.lower():
            return "⏳ Rate limit exceeded. Please wait a moment and try again."
        else:
            return f"Error: {error_msg}"