from fastmcp import FastMCP
import httpx
import os

# Initialize MCP Server
mcp = FastMCP("AQI", host="0.0.0.0", port=8003)

# Load API key for OpenWeatherMap AQI
OPENWEATHERMAP_API_KEY = os.getenv("AQI_API_KEY")

# Geocoding function to get lat/lon from location name using Open-Meteo
async def get_coordinates(location: str):
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1"
    async with httpx.AsyncClient() as client:
        geo_response = await client.get(geo_url)
        geo_data = geo_response.json()

    if "results" not in geo_data or not geo_data["results"]:
        return None, None, None

    result = geo_data["results"][0]
    return result["latitude"], result["longitude"], result["country"]

# AQI Tool
@mcp.tool()
async def get_aqi(location: str) -> str:
    """Get Air Quality Index (AQI) for a given location."""
    if not OPENWEATHERMAP_API_KEY:
        return "❌ AQI API key is missing. Set the 'AQI_API_KEY' environment variable."

    lat, lon, country = await get_coordinates(location)
    if lat is None or lon is None:
        return f"❌ Unable to get coordinates for '{location}'."

    aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={OPENWEATHERMAP_API_KEY}"
    async with httpx.AsyncClient() as client:
        aqi_response = await client.get(aqi_url)
        aqi_data = aqi_response.json()

    if "list" not in aqi_data or not aqi_data["list"]:
        return f"❌ No AQI data found for '{location}'."

    aqi = aqi_data["list"][0]["main"]["aqi"]
    components = aqi_data["list"][0]["components"]

    # AQI level explanation based on OpenWeatherMap
    levels = {
        1: "Good",
        2: "Fair",
        3: "Moderate",
        4: "Poor",
        5: "Very Poor"
    }

    return f"""
📍 Location: {location}, {country}
🗺️ Coordinates: {lat}, {lon}
🌫️ AQI Level: {aqi} ({levels.get(aqi, 'Unknown')})

Pollutants (μg/m3):
- CO: {components['co']}
- NO: {components['no']}
- NO2: {components['no2']}
- O3: {components['o3']}
- SO2: {components['so2']}
- PM2.5: {components['pm2_5']}
- PM10: {components['pm10']}
- NH3: {components['nh3']}
"""

if __name__ == "__main__":
    mcp.run("sse")
