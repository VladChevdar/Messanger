# Vlad Chevdar | CS302 | Aug 25
# Purpose of this program is to report weather to the user
# based on the provided locations or access old reports
from random  import sample
from Weather import *

# Search weather and store it in the user's search history
def search_weather(weather_report):
    city = input()
    state = input()
    city = city.upper() if len(city) < 4 else city.title()
    state = state.upper() if len(state) < 4 else state.title()
    location = (city + ', ' + state)
    #print(f'🌍 Searching for the weather in {location}...')

    if weather_report.get_weather(location):
        weather_report.display()

# Report data based on the option user chooses
def reportWeather():
    report_option = input()
    # Based on the user's choice, create the weather report
    if report_option == '1':
        weather_report = BriefReport()
    elif report_option == '2':
        weather_report = DetailedReport()
    elif report_option == '3':
        weather_report = FunnyReport()
    else:
        print("Error: Invalid option")
        return

    search_weather(weather_report)

# Display a little help for a user
def print_help():
    print("\n" + "="*40)
    print("WELCOME TO WEATHER WIZARD!".center(40))
    print("="*40)
    
    print("\n🌦 SIGN UP 🌦")
    print("- Explore weather data from cities worldwide.")
    print("- Get personalized weather alerts and updates.")
    print("- Benefit: Stay informed and plan your day efficiently!")

    print("\n🌍 LOG IN 🌍")
    print("- Revisit your previous searches effortlessly.")
    print("- Save and manage your favorite cities.")
    print("- Benefit: A tailored weather experience at your fingertips!")

    print("\nWhat would you like to do next? (Choose an option from the main menu!)")

# Display main menu options, and call the necessary functions
def main_menu():
    reportWeather()

if __name__ == '__main__':
    main_menu()