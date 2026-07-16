from flask import Flask, render_template, request, redirect, url_for, session
from utils.itinerary_generator import generate_itinerary
from utils.itinerary_parser import parse_itinerary
from utils.image_fetcher import fetch_images_for_itinerary
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    try:
        city = request.form.get("city", "").strip()
        days = request.form.get("days", "").strip()
        budget = request.form.get("budget", "").strip()
        
        if not city or not days or not budget:
            return render_template("index.html", error="Please fill in all fields")
        
        itinerary = generate_itinerary(city, days, budget)
        
        # Check if AI returned an error message
        if itinerary.startswith("❌") or itinerary.startswith("⏳") or itinerary.startswith("Error"):
            return render_template("index.html", error=itinerary)
        
        # Store in session and redirect to results page
        session['city'] = city
        session['days'] = days
        session['budget'] = budget
        session['itinerary'] = itinerary
        
        return redirect(url_for("results"))
    except Exception as e:
        return render_template("index.html", error=f"Error: {str(e)}")

@app.route("/results")
def results():
    if 'itinerary' not in session:
        return redirect(url_for("home"))
    
    return render_template(
        "results.html",
        city=session.get('city'),
        days=session.get('days'),
        budget=session.get('budget'),
        itinerary=session.get('itinerary')
    )

@app.route("/day-details")
def day_details():
    if 'itinerary' not in session:
        return redirect(url_for("home"))
    
    # Parse itinerary into structured day data
    days_breakdown = parse_itinerary(session.get('itinerary'))
    
    # Fetch images for each day and activity
    days_breakdown = fetch_images_for_itinerary(days_breakdown)
    
    return render_template(
        "day_details.html",
        city=session.get('city'),
        days=session.get('days'),
        budget=session.get('budget'),
        days_breakdown=days_breakdown
    )

@app.route("/new")
def new_plan():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)