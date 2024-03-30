# Vlad Chevdar | CS302 | Aug 25
# Purpose of this file is to have three different weather reports
import requests
from datetime import datetime

# My personal api key from openweathermap.org
API_KEY = '5b853fca1aa27d671dbdcc41185df56a'
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather?'

class Weather:
    def __init__(self):
        self._location = ''
        self._temperature = 0.0
        self._description = ''
        self._wind_speed = 0.0
        self._humidity = 0
        self._pressure = 0.0
        self._temp_min = 0.0
        self._temp_max = 0.0
        self._visibility = 0
        self._wind_direction = 0.0
        self._cloudiness = 0
        self._sunrise = 0
        self._sunset = 0

    def __del__(self):
        self._location = ''
        self._temperature = 0.0
        self._description = ''
        self._wind_speed = 0.0
        self._humidity = 0
        self._pressure = 0.0
        self._temp_min = 0.0
        self._temp_max = 0.0
        self._visibility = 0
        self._wind_direction = 0.0
        self._cloudiness = 0
        self._sunrise = 0
        self._sunset = 0

    # Search the weather using the passed location
    def get_weather(self, location):
        url = BASE_URL + 'q=' + location + '&appid=' + API_KEY + '&units=imperial'
        
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            
            main = data['main']
            wind = data['wind']

            self._location = location
            self._temperature = main['temp']
            self._description = data['weather'][0]['description']
            self._wind_speed = wind['speed']
            self._humidity = main['humidity']
            self._pressure = main['pressure']
            self._temp_min = main['temp_min']
            self._temp_max = main['temp_max']
            self._visibility = data.get('visibility', 0) 
            self._wind_direction = wind['deg']
            self._cloudiness = data['clouds']['all']
            self._sunrise = data['sys']['sunrise']
            self._sunset = data['sys']['sunset']

            return True
        else:
            print(f'Error {response.status_code}: Unable to fetch weather data!')
            return False

class DetailedReport(Weather):
    def __init__(self):
        super().__init__()

    # Display detailed weather report
    def display(self):
        print(f'📍 Location: {self._location}')
        print(f'--- Weather Details --- \n')
        print(f'🌡 Temperature: {self._temperature}°F')
        print(f'🌥 Description: {self._description}')
        print(f'💨 Wind Speed: {self._wind_speed} mph')
        print(f'💧 Humidity: {self._humidity}%')
        print(f'📊 Pressure: {self._pressure} hPa')
        print(f'🔽 Min Temperature: {self._temp_min}°F')
        print(f'🔼 Max Temperature: {self._temp_max}°F')
        print(f'👓 Visibility: {self._visibility/1000*0.62} miles')
        print(f'🧭 Wind Direction: {self._wind_direction}°')
        print(f'☁ Cloudiness: {self._cloudiness}%')
 
        # Convert UNIX timestamp to time
        sunrise_time = datetime.fromtimestamp(self._sunrise).strftime('%H:%M:%S')
        sunset_time = datetime.fromtimestamp(self._sunset).strftime('%H:%M:%S')
        
        print(f'🌅 Sunrise: {sunrise_time}')
        print(f'🌇 Sunset: {sunset_time}')

class BriefReport(Weather):
    def __init__(self):
        super().__init__()

    # Display brief weather report
    def display(self):
        print(f'📍 Location: {self._location}')
        print(f'--- Weather Details --- \n')
        print(f'🌡 Temperature: {self._temperature}°F')
        print(f'🌥 Description: {self._description}')
        print(f'💨 Wind Speed: {self._wind_speed} mph')
        
        # Convert UNIX timestamp to time
        sunrise_time = datetime.fromtimestamp(self._sunrise).strftime('%H:%M:%S')
        sunset_time = datetime.fromtimestamp(self._sunset).strftime('%H:%M:%S')
        
        print(f'🌅 Sunrise: {sunrise_time}')
        print(f'🌇 Sunset: {sunset_time}')

class FunnyReport(Weather):
    def __init__(self):
        super().__init__()

    # Display weather report with some humor
    def display(self):
        print(f'📍 Location: {self._location}')
        print(f'--- Weather Details --- \n')
        print(f'🌡 Temperature: {self._temperature}°F 😅 {self._get_temperature_joke()}')
        print(f'🌥 Description: {self._description} 😂 {self._get_description_joke()}')
        
        print(self._get_sunrise_joke())
        print(self._get_sunset_joke())
    
    # Return temperature joke
    def _get_temperature_joke(self):
        if self._temperature > 100:
            return("You know it's hot when even the ice cream truck is melting!")
        elif self._temperature > 80:
            return("It's so hot, I saw the devil buying sunscreen!")
        elif self._temperature > 60:
            return("It's that confusing weather where you regret both wearing and not wearing a jacket!")
        elif self._temperature > 40:
            return("Perfect weather if you're a penguin or just like wearing three layers of clothes!")
        elif self._temperature > 20:
            return("It's the kind of cold where hot chocolate is a necessity, not a luxury!")
        if self._temperature > 0:
            return("Brrr! It's so cold outside that I saw a polar bear buying a jacket!")
        else:
            return("It's so cold, even the snowmen are migrating south!")

    # Return a joke for description
    def _get_description_joke(self):
        jokes = {
            "clear sky": "Clear skies! Perfect for spotting UFOs.",
            "rain": "Raining so hard even the ducks are using umbrellas.",
            "snow": "Snowflakes today! Remember, each one is unique... just like everyone else.",
            "smoke": "We tried vaping once, and this happened.",
            "fog": "Visibility so low, I might accidentally find Narnia.",
            "cloudy": "So many clouds, the sun's on vacation.",
            "windy": "It's so windy, even the birds are walking!",
            "thunderstorm": "When the skies start drumming, you know the storm is coming."
        }
        return jokes.get(self._description, "What an unusual weather we're having!")

    # Print wind speed with a joke
    def _get_wind_speed_joke(self):
        if self._wind_speed > 10:
            return (f"Wind Speed: {self._wind_speed} mph - The wind's rushing like it's late for a meeting!")
        else:
            return (f'Wind Speed: {self._wind_speed} mph - Even the kites are saying, "Come on, just a little more effort!"')

    # Print sunrise with some joke
    def _get_sunrise_joke(self):
        sunrise_time = datetime.fromtimestamp(self._sunrise).strftime('%H:%M:%S')
        return (f"🌅 Sunrise: {sunrise_time} - 😴 Up before the sun? You deserve a medal... or at least some strong ☕️!")

    # Print sunset with some joke
    def _get_sunset_joke(self):
        sunset_time = datetime.fromtimestamp(self._sunset).strftime('%H:%M:%S')
        return (f"🌇 Sunset: {sunset_time} - 🛌 The sun's taking a break, and it didn't even ask for our permission!")

