from dotenv import load_dotenv
import os
import requests

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise SystemExit("OPENAI_API_KEY is not set. Put it in .env or your environment.")

@tool
def get_weather(query: str) -> str:
    """Get current weather given 'lat, lon' coordinates."""
    try:
        lat_lon = query.strip().split(",")
        latitude = float(lat_lon[0].strip())
        longitude = float(lat_lon[1].strip())
    except Exception:
        # Default to New York if parsing fails
        latitude, longitude = 40.7128, -74.0060

    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}&longitude={longitude}"
        "&current=temperature_2m,wind_speed_10m"
    )
    response = requests.get(url)
    data = response.json()
    temperature = data["current"]["temperature_2m"]
    wind_speed = data["current"]["wind_speed_10m"]
    return f"The current temperature is {temperature}°C with a wind speed of {wind_speed} m/s."

# 1. Create the model, binding the tool
llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools([get_weather])

# 2. Ask your question; the model can choose to call the tool
user_question = (
    "What's the weather like near 41.7151, 44.8271 (Tbilisi, Georgia)? "
    "Use coordinates '41.7151, 44.8271'."
)

response = llm_with_tools.invoke(user_question)

print("Raw model response:", response)
