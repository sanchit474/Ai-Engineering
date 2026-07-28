from datetime import datetime
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Calculator-datetime")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    return a - b
@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b

@mcp.tool()
def divide(a: int, b: int) -> float:
    """Divide two numbers"""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

@mcp.tool()
def square(number: int) -> int:
    """Return the square of a number."""
    return number * number


@mcp.tool()
def cube(number: int) -> int:
    """Return the cube of a number."""
    return number ** 3

@mcp.tool()
def current_time() -> str:
    """Get current time"""

    return datetime.now().strftime("%H:%M:%S")

@mcp.tool()
def current_date() -> str:
    """Get current date"""
    return datetime.now().strftime("%Y-%m-%d")

@mcp.tool()
def current_day() -> str:
    """Get current day of the week"""
    return datetime.now().strftime("%A")

# --- New Weather Tool ---
@mcp.tool()
async def get_weather(location: str) -> str:
    """
    Get real-time weather conditions and current temperature for a city or location name.

    Args:
        location: City or location name (e.g. 'London', 'Tokyo', 'New York').
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # 1. Geocode location name to latitude/longitude
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1&language=en&format=json"
            geo_resp = await client.get(geo_url)
            geo_data = geo_resp.json()

            if not geo_data.get("results"):
                return f"Error: Could not find location coordinates for '{location}'."

            city_info = geo_data["results"][0]
            lat = city_info["latitude"]
            lon = city_info["longitude"]
            city_name = city_info.get("name", location)
            country = city_info.get("country", "")

            # 2. Fetch current weather data from Open-Meteo
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            w_resp = await client.get(weather_url)
            w_data = w_resp.json()

            current = w_data.get("current_weather")
            if not current:
                return f"Error: Failed to fetch current weather data for '{location}'."

            temp = current.get("temperature")
            wind = current.get("windspeed")
            units = w_data.get("current_weather_units", {})
            temp_unit = units.get("temperature", "°C")
            wind_unit = units.get("windspeed", "km/h")

            return f"  {city_name}, {country}: {temp}{temp_unit}, Wind speed: {wind} {wind_unit}."

        except Exception as e:
            return f"Error executing weather search: {e}"


if __name__ == "__main__":
    # Specify transport='stdio' explicitly
    mcp.run(transport="stdio")