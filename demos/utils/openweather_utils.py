import os

import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up OpenAI API key
OPEN_WEATHER_API_KEY = os.getenv("OPEN_WEATHER_API_KEY")
if not OPEN_WEATHER_API_KEY:
    raise ValueError(
        "Please set the OPEN_WEATHER_API_KEY environment variable."
    )


def get_current_weather(location: str) -> dict:
    """
    Get the current weather for a given city using OpenWeatherMap API.

    Args:
        location (str): Name of the city.
        api_key (str): Your OpenWeatherMap API key.

    Returns:
        dict: Weather data for the city.
    """
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": location,
        "appid": OPEN_WEATHER_API_KEY,
        "units": "metric",  # Use 'imperial' for Fahrenheit
        "lang": "en",  # Language for the response
    }

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching weather data: {response.status_code}")


def format_weather_data(weather_data: dict) -> str:
    """
    Format the weather data into a readable string.

    Args:
        weather_data (dict): Weather data from OpenWeatherMap API.

    Returns:
        str: Formatted weather information.
    """
    city = weather_data["name"]
    country = weather_data["sys"]["country"]
    temperature = weather_data["main"]["temp"]
    humidity = weather_data["main"]["humidity"]
    description = weather_data["weather"][0]["description"]

    return (
        f"Current weather in {city}, {country}:\n"
        f"Temperature: {temperature}°C\n"
        f"Humidity: {humidity}%\n"
        f"Description: {description.capitalize()}"
    )
