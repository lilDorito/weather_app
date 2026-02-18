# Weather SaaS API

A Python-based Weather SaaS deployed on AWS EC2, built with Flask and uWSGI.

## Features
- Get weather data for any location and date
- AI-powered UAV flight safety recommendations (via Groq/LLaMA)

## Endpoints

### Weather Data Endpoint
`POST /content/api/v1/integration/generate`
```json
{
    "token": "your_token",
    "requester_name": "Your Name",
    "location": "London,UK",
    "date": "2026-02-18"
}
```

### UAV Flight Advice Endpoint
`POST /content/api/v1/integration/uav-advice`
```json
{
    "token": "your_token",
    "requester_name": "Your Name",
    "location": "London,UK",
    "date": "2026-02-18"
}
```

> Location can be any city, e.g. `"London,UK"`, `"New York,US"`, `"Paris,France"`, `"Kyiv,Ukraine"`

## Setup

### Requirements
- Python 3.8+
- pip

Install dependencies:
```bash
pip install -r requirements.txt
```

### Environment Variables
```bash
export API_TOKEN="your_token"
export VISUAL_CROSSING_KEY="your_visual_crossing_key"
export GROQ_API_KEY="your_groq_key"
```

### Run with uWSGI
```bash
uwsgi --http 0.0.0.0:8000 --wsgi-file weather_app.py --callable app --processes 4 --threads 2
```

## APIs Used
- [Visual Crossing](https://www.visualcrossing.com/) - weather data
- [Groq / LLaMA 3.3](https://console.groq.com/) - AI UAV flight recommendations
