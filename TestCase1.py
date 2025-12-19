#forked from kinaio
from dotenv import load_dotenv
import os
import requests

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, create_react_agent

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
print("DEBUG OPENAI_API_KEY:", repr(OPENAI_API_KEY))  # remove after it works
if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY not found in environment variables")
    raise SystemExit("Set OPENAI_API_KEY in .env or OS environment")

@tool
def get_weather(query: str) -> str:
    """Get current weather given 'lat, lon' coordinates."""
    try:
        lat_lon = query.strip().split(',')
        latitude = float(lat_lon[0].strip())
        longitude = float(lat_lon[1].strip())
    except Exception:
        latitude, longitude = 40.7128, -74.0060  # fallback: New York

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

# LLM (key is taken from OPENAI_API_KEY env variable)
llm = ChatOpenAI(model="gpt-4o-mini")

tools = [get_weather]
tool_node = ToolNode(tools)

graph = create_react_agent(llm, tools)

inputs = {
    "messages": [
        {
            "role": "user",
            "content": (
                "What's the weather like near 41.7151, 44.8271 "
                "(Tbilisi, Georgia)? Use coordinates '41.7151, 44.8271'."
            ),
        }
    ]
}

result = graph.invoke(inputs)
print(result["messages"][-1]["content"])
