from flask import Flask, request, jsonify
import requests
from datetime import datetime
import os
import json
from groq import Groq

app = Flask(__name__)
API_TOKEN = os.environ.get("API_TOKEN")
VISUAL_CROSSING_KEY = os.environ.get("VISUAL_CROSSING_KEY")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

def fetch_weather(location, date):
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location}/{date}?unitGroup=metric&key={VISUAL_CROSSING_KEY}&contentType=json"
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return response.json()

@app.route("/content/api/v1/integration/generate", methods=["POST"])
def get_weather():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    token = data.get("token")
    requester_name = data.get("requester_name")
    location = data.get("location")
    date = data.get("date")

    if token != API_TOKEN:
        return jsonify({"error": "Invalid token"}), 403

    weather_data = fetch_weather(location, date)
    if not weather_data:
        return jsonify({"error": "Weather API error"}), 500

    day = weather_data["days"][0]
    return jsonify({
        "requester_name": requester_name,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "location": location,
        "date": date,
        "weather": {
            "temp_c": day.get("temp"),
            "wind_kph": day.get("windspeed"),
            "pressure_mb": day.get("pressure"),
            "humidity": day.get("humidity"),
            "description": day.get("description")
        }
    })

@app.route("/content/api/v1/integration/uav-advice", methods=["POST"])
def uav_advice():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    token = data.get("token")
    requester_name = data.get("requester_name")
    location = data.get("location")
    date = data.get("date")

    if token != API_TOKEN:
        return jsonify({"error": "Invalid token"}), 403

    weather_data = fetch_weather(location, date)
    if not weather_data:
        return jsonify({"error": "Weather API error"}), 500

    day = weather_data["days"][0]
    weather_summary = {
        "temp_c": day.get("temp"),
        "wind_kph": day.get("windspeed"),
        "pressure_mb": day.get("pressure"),
        "humidity": day.get("humidity"),
        "description": day.get("description"),
        "visibility": day.get("visibility"),
        "cloudcover": day.get("cloudcover"),
        "precipprob": day.get("precipprob")
    }

    prompt = f"""You are a UAV/drone flight safety expert. Based on the following weather data for {location} on {date}, provide UAV flight recommendations.

Weather data:
- Temperature: {weather_summary['temp_c']}°C
- Wind speed: {weather_summary['wind_kph']} km/h
- Pressure: {weather_summary['pressure_mb']} mb
- Humidity: {weather_summary['humidity']}%
- Cloud cover: {weather_summary['cloudcover']}%
- Precipitation probability: {weather_summary['precipprob']}%
- Visibility: {weather_summary['visibility']} km
- Description: {weather_summary['description']}

Respond in JSON format only, no extra text, no markdown, no backticks:
{{
  "flight_recommended": true or false,
  "safety_rating": "Safe / Marginal / Unsafe",
  "best_time_window": "e.g. 10:00-13:00 UTC",
  "recommended_max_altitude_m": number,
  "reasons": ["reason 1", "reason 2"],
  "tips": ["tip 1", "tip 2"]
}}"""

    client = Groq(api_key=GROQ_API_KEY)
    message = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024
    )

    ai_response = json.loads(message.choices[0].message.content)

    return jsonify({
        "requester_name": requester_name,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "location": location,
        "date": date,
        "weather": weather_summary,
        "uav_advice": ai_response
    })

if __name__ == "__main__":
    app.run()
