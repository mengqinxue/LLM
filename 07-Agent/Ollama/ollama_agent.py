import ollama
import requests


# Weather query tool function
def get_weather(location: str):
    # Use Open-Meteo's geocoding API to get latitude and longitude
    geocode_url = "https://geocoding-api.open-meteo.com/v1/search"
    weather_url = "https://api.open-meteo.com/v1/forecast"

    # Get city coordinates
    response = requests.get(geocode_url, params={"name": location, "count": 1})
    data = response.json()

    if not data.get("results"):
        return f"No information found for location '{location}'."

    result = data["results"][0]
    latitude = result["latitude"]
    longitude = result["longitude"]

    # Get weather information
    weather_response = requests.get(weather_url, params={
        "latitude": latitude,
        "longitude": longitude,
        "current_weather": True
    })

    weather_data = weather_response.json()
    current_weather = weather_data["current_weather"]

    return {
        "temperature": current_weather["temperature"],
        "windspeed": current_weather["windspeed"],
        "weathercode": current_weather["weathercode"]
    }

# Tool mapping table
tools = {
    "get_weather": get_weather
}

# Weather description mapping
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snowfall",
    73: "Moderate snowfall",
    75: "Heavy snowfall",
    95: "Thunderstorm"
}

# Main program
def main():
    print("Welcome to the weather assistant! You can ask me about the weather.")
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        # Let the model decide whether to call a tool
        prompt = f"""
                    You are an AI assistant. Please determine if the user's question requires using the weather 
                    lookup function. If yes, please provide the tool name and parameters; otherwise, reply directly.
                    
                    Example:
                    User asks: "What is the weather in Beijing today?"
                    Your response should be:
                    Call tool: get_weather
                    Parameters: {{"location": "Beijing"}}
                    
                    Now analyze the following user input:
                    "{user_input}"
                """

        response = ollama.generate(model="deepseek-r1:1.5b", prompt=prompt)
        tool_call = response['response'].strip()

        if tool_call.startswith("Call tool:"):
            try:
                tool_name = tool_call.split(":")[1].split("\n")[0].strip()
                location = eval(tool_call.split("Parameters:")[1].strip())["location"]
                print(f"Calling {tool_name} to get weather in {location}...")
                weather_data = tools[tool_name](location)

                if isinstance(weather_data, dict):
                    desc = WEATHER_CODES.get(int(weather_data["weathercode"]), "Unknown weather")
                    reply = f"The current temperature in {location} is {weather_data['temperature']}°C, wind speed is {weather_data['windspeed']} km/h, and the weather condition is: {desc}."
                else:
                    reply = weather_data
            except Exception as e:
                reply = f"An error occurred: {str(e)}"

        else:
            # Model replies directly
            reply = ollama.generate(model="deepseek-r1:1.5b", prompt=user_input)['response']

        print(f"\nAssistant: {reply}")

if __name__ == "__main__":
    main()